from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
)

ARGUMENTS = [
    DeclareLaunchArgument(
        'setup_path',
        default_value='/root/workspace/src'
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
