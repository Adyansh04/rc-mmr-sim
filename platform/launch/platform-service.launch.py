from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable, FindExecutable, PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # Include Packages
    pkg_clearpath_common = FindPackageShare('rc_common')

    # Declare launch files
    launch_file_platform = PathJoinSubstitution([
        pkg_clearpath_common, 'launch', 'platform.launch.py'])

    # Include launch files
    launch_platform = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([launch_file_platform]),
        launch_arguments=
            [
                (
                    'setup_path'
                    ,
                    '.'
                )
                ,
                (
                    'use_sim_time'
                    ,
                    'true'
                )
                ,
                (
                    'namespace'
                    ,
                    'rc'
                )
                ,
                (
                    'enable_ekf'
                    ,
                    'true'
                )
                ,
                (
                    'use_manipulation_controllers'
                    ,
                    'true'
                )
                ,
            ]
    )

    # Nodes
    node_cmd_vel_bridge = Node(
        name='cmd_vel_bridge',
        executable='parameter_bridge',
        package='ros_gz_bridge',
        namespace='rc',
        output='screen',
        arguments=
            [
                'rc/cmd_vel@geometry_msgs/msg/TwistStamped[gz.msgs.Twist'
                ,
                '/model/rc/robot/cmd_vel@geometry_msgs/msg/TwistStamped]gz.msgs.Twist'
                ,
            ]
        ,
        remappings=
            [
                (
                    'rc/cmd_vel'
                    ,
                    'cmd_vel'
                )
                ,
                (
                    '/model/rc/robot/cmd_vel'
                    ,
                    'platform/cmd_vel'
                )
                ,
            ]
        ,
        parameters=
            [
                {
                    'use_sim_time': True
                    ,
                }
                ,
            ]
        ,
    )

    node_odom_base_tf_bridge = Node(
        name='odom_base_tf_bridge',
        executable='parameter_bridge',
        package='ros_gz_bridge',
        namespace='rc',
        output='screen',
        arguments=
            [
                '/model/rc/robot/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'
                ,
            ]
        ,
        remappings=
            [
                (
                    '/model/rc/robot/tf'
                    ,
                    'tf'
                )
                ,
            ]
        ,
        parameters=
            [
                {
                    'use_sim_time': True
                    ,
                }
                ,
            ]
        ,
    )

    # Create LaunchDescription
    ld = LaunchDescription()
    ld.add_action(launch_platform)
    ld.add_action(node_cmd_vel_bridge)
    ld.add_action(node_odom_base_tf_bridge)
    return ld
