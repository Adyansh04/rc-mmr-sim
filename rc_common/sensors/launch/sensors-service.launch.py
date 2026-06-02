from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable, FindExecutable, PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # Include Packages

    launch_file_lidar2d_0 = PathJoinSubstitution([
        FindPackageShare('rc_common'), 'sensors/launch/lidar2d_0.launch.py'
    ])
    launch_file_lidar2d_1 = PathJoinSubstitution([
        FindPackageShare('rc_common'), 'sensors/launch/lidar2d_1.launch.py'
    ])
    launch_file_camera_0 = PathJoinSubstitution([
        FindPackageShare('rc_common'), 'sensors/launch/camera_0.launch.py'
    ])
    launch_file_imu_0 = PathJoinSubstitution([
        FindPackageShare('rc_common'), 'sensors/launch/imu_0.launch.py'
    ])

    # Include launch files
    launch_lidar2d_0 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([launch_file_lidar2d_0]),
    )

    launch_lidar2d_1 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([launch_file_lidar2d_1]),
    )

    launch_camera_0 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([launch_file_camera_0]),
    )

    launch_imu_0 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([launch_file_imu_0]),
    )

    # Create LaunchDescription
    ld = LaunchDescription()
    ld.add_action(launch_lidar2d_0)
    ld.add_action(launch_lidar2d_1)
    ld.add_action(launch_camera_0)
    ld.add_action(launch_imu_0)
    return ld
