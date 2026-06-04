import os
import xacro
import tempfile
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from webots_ros2_driver.webots_launcher import WebotsLauncher, Ros2SupervisorLauncher
from webots_ros2_driver.webots_controller import WebotsController
from webots_ros2_driver.urdf_spawner import URDFSpawner

def launch_setup(context, *args, **kwargs):
    pkg_rc_webots = get_package_share_directory('rc_webots')
    pkg_rc_common = get_package_share_directory('rc_common')
    pkg_rc_manipulators = get_package_share_directory('rc_manipulators')
    pkg_rc_nav2_demos = get_package_share_directory('rc_nav2_demos')
    pkg_rc_viz = get_package_share_directory('rc_viz')

    # Resolve paths as strings at runtime
    world_path = context.perform_substitution(LaunchConfiguration('world'))
    gazebo_controllers_path = context.perform_substitution(LaunchConfiguration('gazebo_controllers'))
    namespace = context.perform_substitution(LaunchConfiguration('namespace'))

    # 1. Start Webots Simulator
    webots = WebotsLauncher(
        world=world_path,
        mode='realtime'
    )

    # 1.5 Start the ROS 2 Supervisor Node
    ros2_supervisor = Ros2SupervisorLauncher()

    # 2. Path to the robot description URDF/Xacro containing WebotsControl
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

    # Write the compiled URDF to a temporary file to avoid CLI character limits
    urdf_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.urdf')
    urdf_temp_file.write(robot_description_content.encode('utf-8'))
    urdf_temp_file.close()
    urdf_file_path = urdf_temp_file.name

    # Spawn the robot dynamically into the Webots world
    spawn_urdf = URDFSpawner(
        name='a300_mmr',
        robot_description=robot_description_content,
        translation='0 0 0.15',  # Lift it slightly to prevent wheels clipping into the floor on spawn
        rotation='0 0 1 0'
    )

    # 3. Webots controller driver node with remappings
    webots_robot_driver = WebotsController(
        robot_name='a300_mmr',
        namespace=namespace,
        parameters=[
            {'robot_description': urdf_file_path},
            {'use_sim_time': True},
            gazebo_controllers_path
        ],
        remappings=[
            ('~/odom', 'platform/odom'),
            ('~/cmd_vel', 'platform/cmd_vel'),
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static'),
            ('/dynamic_joint_states', 'platform/dynamic_joint_states'),
            ('joint_states', 'platform/joint_states'),
            ('~/reference', 'platform/cmd_vel'),
            ('~/odometry', 'platform/odom'),
        ]
    )

    # 4. Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace=namespace,
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': True
        }],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static'),
            ('joint_states', 'platform/joint_states'),
        ]
    )

    # 5. Controller Spawners
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        namespace=namespace,
        arguments=['joint_state_broadcaster', '-c', 'a300_mmr', '--controller-manager-timeout', '60'],
        output='screen'
    )

    platform_velocity_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        namespace=namespace,
        arguments=['platform_velocity_controller', '-c', 'a300_mmr', '--controller-manager-timeout', '60'],
        output='screen'
    )

    arm_0_joint_trajectory_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        namespace=namespace,
        arguments=['arm_0_joint_trajectory_controller', '-c', 'a300_mmr', '--controller-manager-timeout', '60'],
        output='screen'
    )

    arm_0_gripper_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        namespace=namespace,
        arguments=['arm_0_gripper_controller', '-c', 'a300_mmr', '--controller-manager-timeout', '60'],
        output='screen'
    )

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

    # 7. MoveIt 2 launch setup from rc_manipulators
    launch_moveit = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_rc_manipulators, 'launch', 'moveit.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items(),
        condition=IfCondition(LaunchConfiguration('moveit'))
    )

    # 8. Nav2 launch setup from rc_nav2_demos
    launch_nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_rc_nav2_demos, 'launch', 'nav2.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items(),
        condition=IfCondition(LaunchConfiguration('nav2'))
    )

    return [
        webots,
        ros2_supervisor,
        spawn_urdf,
        webots_robot_driver,
        robot_state_publisher,
        joint_state_broadcaster_spawner,
        platform_velocity_controller_spawner,
        arm_0_joint_trajectory_controller_spawner,
        arm_0_gripper_controller_spawner,
        launch_rviz,
        launch_moveit,
        launch_nav2
    ]

def generate_launch_description():
    pkg_rc_webots = get_package_share_directory('rc_webots')
    pkg_rc_common = get_package_share_directory('rc_common')

    # Declare launch arguments
    namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value='rc',
        description='Robot namespace'
    )

    gazebo_controllers_arg = DeclareLaunchArgument(
        'gazebo_controllers',
        default_value=os.path.join(pkg_rc_common, 'platform', 'config', 'control.yaml'),
        description='Path to the controller configuration YAML file'
    )

    world_arg = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(pkg_rc_webots, 'worlds', 'empty_world.wbt'),
        description='Path to the Webots world file'
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
        gazebo_controllers_arg,
        world_arg,
        rviz_arg,
        moveit_arg,
        nav2_arg,
        OpaqueFunction(function=launch_setup)
    ])
