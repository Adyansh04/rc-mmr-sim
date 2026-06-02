from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.substitutions import FindPackageShare


ARGUMENTS = [
    DeclareLaunchArgument(
        'setup_path',
        default_value=FindPackageShare('rc_common')
    ),

    DeclareLaunchArgument(
        'use_sim_time',
        choices=['true', 'false'],
        default_value='false',
        description='Use simulation time'
    ),

    DeclareLaunchArgument(
        'namespace',
        default_value='',
        description='Robot namespace'
    ),
]

def generate_launch_description():
    ld = LaunchDescription(ARGUMENTS)
    return ld
