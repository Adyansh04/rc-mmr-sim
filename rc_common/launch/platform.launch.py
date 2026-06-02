from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    IncludeLaunchDescription,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution
)
from launch_ros.actions import PushRosNamespace
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # Packages
    pkg_rc_control = FindPackageShare('rc_control')
    pkg_rc_platform_description = FindPackageShare('rc_platform_description')

    # Launch Arguments
    arg_setup_path = DeclareLaunchArgument(
        'setup_path',
        default_value=FindPackageShare('rc_common')
    )

    arg_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        choices=['true', 'false'],
        default_value='false',
        description='Use simulation time'
    )

    arg_namespace = DeclareLaunchArgument(
        'namespace',
        default_value='',
        description='Robot namespace'
    )

    arg_enable_ekf = DeclareLaunchArgument(
        'enable_ekf',
        default_value='true',
        choices=['true', 'false'],
        description='Enable localization via EKF node'
    )

    # Launch Configurations
    setup_path = FindPackageShare('rc_common')
    use_sim_time = LaunchConfiguration('use_sim_time')
    namespace = LaunchConfiguration('namespace')
    enable_ekf = LaunchConfiguration('enable_ekf')

    # Launch files
    launch_file_platform_description = PathJoinSubstitution([
      pkg_rc_platform_description,
      'launch',
      'description.launch.py'])

    launch_file_control = PathJoinSubstitution([
      pkg_rc_control,
      'launch',
      'control.launch.py'])

    launch_file_localization = PathJoinSubstitution([
      pkg_rc_control,
      'launch',
      'localization.launch.py'])

    launch_file_teleop_base = PathJoinSubstitution([
      pkg_rc_control,
      'launch',
      'teleop_base.launch.py'])

    launch_file_teleop_joy = PathJoinSubstitution([
      pkg_rc_control,
      'launch',
      'teleop_joy.launch.py'])

    group_platform_action = GroupAction(
        actions=[
            PushRosNamespace(namespace),

            IncludeLaunchDescription(
              PythonLaunchDescriptionSource(launch_file_platform_description),
              launch_arguments=[
                ('setup_path', setup_path),
                ('use_sim_time', use_sim_time),
                ('namespace', namespace),
              ]
            ),

            # Launch rc_control/control.launch.py which is just robot_localization.
            IncludeLaunchDescription(
              PythonLaunchDescriptionSource(launch_file_control),
              launch_arguments=[
                ('setup_path', setup_path),
                ('use_sim_time', use_sim_time),
              ]
            ),

            # Launch localization (ekf node)
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(launch_file_localization),
                launch_arguments=[
                  ('setup_path', setup_path),
                  ('use_sim_time', use_sim_time),
                  ('enable_ekf', enable_ekf)
                ]
            ),

            # Launch rc_control/teleop_base.launch.py which is various ways to tele-op
            # the robot but does not include the joystick. Also, has a twist mux.
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(launch_file_teleop_base),
                launch_arguments=[
                  ('setup_path', setup_path),
                  ('use_sim_time', use_sim_time),
                ]
            ),

            # Launch rc_control/teleop_joy.launch.py which is tele-operation using a
            # physical joystick.
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(launch_file_teleop_joy),
                launch_arguments=[
                  ('setup_path', setup_path),
                  ('use_sim_time', use_sim_time),
                ]
            ),
        ]
    )

    ld = LaunchDescription()
    ld.add_action(arg_setup_path)
    ld.add_action(arg_use_sim_time)
    ld.add_action(arg_namespace)
    ld.add_action(arg_enable_ekf)
    ld.add_action(group_platform_action)
    return ld
