import os
import xacro
import tempfile
import launch
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from webots_ros2_driver.webots_launcher import WebotsLauncher
from webots_ros2_driver.webots_controller import WebotsController
from webots_ros2_driver.urdf_spawner import URDFSpawner, get_webots_driver_node
from webots_ros2_driver.wait_for_controller_connection import WaitForControllerConnection

def launch_setup(context, *args, **kwargs):
    pkg_rc_webots = get_package_share_directory('rc_webots')
    pkg_rc_common = get_package_share_directory('rc_common')
    pkg_rc_manipulators = get_package_share_directory('rc_manipulators')
    pkg_rc_nav2_demos = get_package_share_directory('rc_nav2_demos')
    pkg_rc_viz = get_package_share_directory('rc_viz')

    # Resolve paths as strings at runtime
    world_path = context.perform_substitution(LaunchConfiguration('world'))
    controllers_path = context.perform_substitution(LaunchConfiguration('controllers'))
    namespace = context.perform_substitution(LaunchConfiguration('namespace'))
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # 1. Start Webots Simulator
    webots = WebotsLauncher(
        world=world_path,
        mode='realtime',
        ros2_supervisor=True
    )

    # 2. Path to the robot description URDF/Xacro
    robot_description_path = os.path.join(pkg_rc_common, 'robot.urdf.xacro')
    robot_description_content = xacro.process_file(
        robot_description_path,
        mappings={'is_sim': 'true'}
    ).toxml()

    # FIX 1: Strip 'file://' from mesh paths so Webots reads them as absolute Unix paths
    robot_description_content = robot_description_content.replace('file://', '')

    # FIX 2: Force the UR5e arm to use Webots control instead of Gazebo
    robot_description_content = robot_description_content.replace(
        '<plugin>gz_ros2_control/GazeboSimSystem</plugin>',
        '<plugin>webots_ros2_control::Ros2ControlSystem</plugin>'
    )
    robot_description_content = robot_description_content.replace(
        '<plugin>ign_ros2_control/IgnitionSystem</plugin>',
        '<plugin>webots_ros2_control::Ros2ControlSystem</plugin>'
    )

    import re

    def resolve_package_paths(match):
        package_name = match.group(1)
        rest_of_path = match.group(2)
        try:
            package_path = get_package_share_directory(package_name)
            return package_path + rest_of_path
        except Exception:
            return match.group(0)

    robot_description_content = re.sub(
        r'package://([^/]+)(/[^"\']*)',
        resolve_package_paths,
        robot_description_content
    )

    # XML merge: combine valid ros2_control joints and all webots blocks into single blocks.
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(robot_description_content)

        # 1. Merge all <webots> elements into a single <webots> block
        webots_elements = root.findall('.//webots')
        merged_webots = ET.Element('webots')
        for elem in webots_elements:
            for child in list(elem):
                merged_webots.append(child)
            # Remove old webots element from its parent
            for parent in root.iter():
                if elem in parent:
                    parent.remove(elem)
                    break

        # 2. Add the ros2_control plugin to the merged <webots> block
        control_plugin = ET.Element('plugin', {'type': 'webots_ros2_control::Ros2Control'})
        merged_webots.append(control_plugin)
        root.append(merged_webots)

        physical_joint_names = {
            joint.get('name')
            for joint in root.findall('joint')
            if joint.get('name')
        }
        control_elements = root.findall('.//ros2_control')
        merged_control = ET.Element('ros2_control', {'name': 'WebotsControl', 'type': 'system'})
        hardware = ET.SubElement(merged_control, 'hardware')
        plugin = ET.SubElement(hardware, 'plugin')
        plugin.text = 'webots_ros2_control::Ros2ControlSystem'

        seen_joint_names = set()
        skipped_control_names = []
        for elem in control_elements:
            for child in list(elem):
                if child.tag != 'joint':
                    continue
                joint_name = child.get('name')
                has_interfaces = (
                    child.findall('command_interface')
                    or child.findall('state_interface')
                )
                if (
                    not joint_name
                    or joint_name not in physical_joint_names
                    or joint_name in seen_joint_names
                    or not has_interfaces
                ):
                    if joint_name and joint_name not in seen_joint_names:
                        skipped_control_names.append(joint_name)
                    continue
                merged_control.append(child)
                seen_joint_names.add(joint_name)
            # Remove old element from its parent
            for parent in root.iter():
                if elem in parent:
                    parent.remove(elem)
                    break
        root.append(merged_control)
        robot_description_content = ET.tostring(root, encoding='utf-8').decode('utf-8')
        if skipped_control_names:
            print(
                'Skipped ros2_control entries absent from the URDF joint tree: '
                + ', '.join(sorted(set(skipped_control_names)))
            )
    except Exception as e:
        print("ERROR merging ros2_control blocks:", e)

    # Write the scrubbed URDF to a temporary file
    urdf_file = tempfile.NamedTemporaryFile(delete=False, suffix='.urdf', mode='w')
    urdf_file.write(robot_description_content)
    urdf_file.close()

    spawn_URDF_a300 = URDFSpawner(
        name='a300-00000',
        urdf_path=urdf_file.name,
        translation='0 0 0.25',
        rotation='0 0 1 0',
    )

    # 3. Robot state publisher — use the real robot description
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        namespace=namespace,
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': use_sim_time,
        }],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static'),
            ('joint_states', 'platform/joint_states'),
        ],
    )

    # 4. Webots controller driver node
    webots_robot_driver = WebotsController(
        robot_name='a300-00000',
        namespace=namespace,
        output='screen',
        parameters=[
            {
                'robot_description': urdf_file.name,
                'use_sim_time': True,
                'set_robot_state_publisher': False,
            },
            controllers_path
        ],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static'),
            ('joint_states', 'platform/joint_states')
        ],
        respawn=True
    )

    # 5. Controller Spawners — use explicit -c to point to the namespaced
    #    controller_manager, matching the UR demo pattern.
    controller_manager_timeout = ['--controller-manager-timeout', '500']
    controller_manager_prefix = 'python.exe' if os.name == 'nt' else ''
    cm_name = namespace + '/controller_manager'

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        output='screen',
        prefix=controller_manager_prefix,
        arguments=['joint_state_broadcaster', '-c', cm_name] + controller_manager_timeout,
    )

    platform_velocity_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        output='screen',
        prefix=controller_manager_prefix,
        arguments=['platform_velocity_controller', '-c', cm_name] + controller_manager_timeout,
    )

    arm_0_joint_trajectory_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        output='screen',
        prefix=controller_manager_prefix,
        arguments=['arm_0_joint_trajectory_controller', '-c', cm_name] + controller_manager_timeout,
    )

    arm_0_gripper_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        output='screen',
        prefix=controller_manager_prefix,
        arguments=['arm_0_gripper_controller', '-c', cm_name] + controller_manager_timeout,
    )

    ros_control_spawners = [
        joint_state_broadcaster_spawner,
        platform_velocity_controller_spawner,
        arm_0_joint_trajectory_controller_spawner,
        arm_0_gripper_controller_spawner,
    ]

    # 6. RViz
    launch_rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_rc_viz, 'launch', 'view_robot.launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'namespace': namespace
        }.items(),
        condition=IfCondition(LaunchConfiguration('rviz'))
    )

    # 7. MoveIt 2
    launch_moveit = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_rc_manipulators, 'launch', 'moveit.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items(),
        condition=IfCondition(LaunchConfiguration('moveit'))
    )

    # 8. Nav2
    launch_nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_rc_nav2_demos, 'launch', 'nav2.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items(),
        condition=IfCondition(LaunchConfiguration('nav2'))
    )

    # Use WaitForControllerConnection to delay spawners and optional
    # nodes until the Webots driver is fully connected — exactly like
    # the Tiago demo does.
    waiting_nodes = WaitForControllerConnection(
        target_driver=webots_robot_driver,
        nodes_to_start=ros_control_spawners + [launch_rviz, launch_moveit, launch_nav2]
    )

    return [
        webots,
        webots._supervisor,
        spawn_URDF_a300,
        robot_state_publisher,

        # Launch the driver node once the URDF robot is spawned
        launch.actions.RegisterEventHandler(
            event_handler=launch.event_handlers.OnProcessIO(
                target_action=spawn_URDF_a300,
                on_stdout=lambda event: get_webots_driver_node(event, webots_robot_driver),
            )
        ),

        # Wait for driver connection, then start spawners + optional nodes
        waiting_nodes,

        # Kill everything when Webots exits
        launch.actions.RegisterEventHandler(
            event_handler=launch.event_handlers.OnProcessExit(
                target_action=webots,
                on_exit=[
                    launch.actions.EmitEvent(event=launch.events.Shutdown())
                ],
            )
        )
    ]

def generate_launch_description():
    pkg_rc_webots = get_package_share_directory('rc_webots')

    # Declare launch arguments
    namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value='rc',
        description='Robot namespace'
    )

    controllers_arg = DeclareLaunchArgument(
        'controllers',
        default_value=os.path.join(pkg_rc_webots, 'config', 'webots_control.yaml'),
        description='Path to the controller configuration YAML file'
    )

    world_arg = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(pkg_rc_webots, 'worlds', 'universal_robot.wbt'),
        description='Path to the Webots world file'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        choices=['true', 'false'],
        description='Use simulation clock'
    )

    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='false',
        choices=['true', 'false'],
        description='Whether to start RViz'
    )

    moveit_arg = DeclareLaunchArgument(
        'moveit',
        default_value='false',
        choices=['true', 'false'],
        description='Whether to start MoveIt'
    )

    nav2_arg = DeclareLaunchArgument(
        'nav2',
        default_value='false',
        choices=['true', 'false'],
        description='Whether to start Nav2'
    )

    return LaunchDescription([
        namespace_arg,
        controllers_arg,
        world_arg,
        use_sim_time_arg,
        rviz_arg,
        moveit_arg,
        nav2_arg,
        OpaqueFunction(function=launch_setup)
    ])
