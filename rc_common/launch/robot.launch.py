import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def launch_setup(context, *args, **kwargs):
    # Parse configurations
    mapping = context.perform_substitution(LaunchConfiguration('mapping')) == 'true'
    nav2 = context.perform_substitution(LaunchConfiguration('nav2')) == 'true'
    moveit = context.perform_substitution(LaunchConfiguration('moveit')) == 'true'
    rviz = context.perform_substitution(LaunchConfiguration('rviz')) == 'true'
    map_file = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')

    pkg_rc_nav2_demos = get_package_share_directory('rc_nav2_demos')
    pkg_rc_manipulators = get_package_share_directory('rc_manipulators')
    pkg_rc_viz = get_package_share_directory('rc_viz')
    pkg_rc_webots = get_package_share_directory('rc_webots')

    actions = []

    actions.append(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(pkg_rc_webots, 'launch', 'webots_sim.launch.py'))
        )
    )

    if mapping:
        # Mapping Mode: Launch Nav2 + SLAM + RViz (view_navigation)
        actions.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_rc_nav2_demos, 'launch', 'nav2.launch.py')
                ),
                launch_arguments={'use_sim_time': use_sim_time}.items(),
            )
        )
        actions.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(pkg_rc_nav2_demos, 'launch', 'slam.launch.py')
                ),
                launch_arguments={'use_sim_time': use_sim_time}.items(),
            )
        )
        if rviz:
            actions.append(
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(
                        os.path.join(pkg_rc_viz, 'launch', 'view_navigation.launch.py')
                    ),
                    launch_arguments={'use_sim_time': use_sim_time, 'namespace': '/rc'}.items(),
                )
            )
    else:
        # Navigation / Localization Mode
        if nav2:
            actions.append(
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(
                        os.path.join(pkg_rc_nav2_demos, 'launch', 'nav2.launch.py')
                    ),
                    launch_arguments={'use_sim_time': use_sim_time}.items(),
                )
            )
            actions.append(
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(
                        os.path.join(pkg_rc_nav2_demos, 'launch', 'localization.launch.py')
                    ),
                    launch_arguments={'use_sim_time': use_sim_time, 'map': map_file}.items(),
                )
            )
            if rviz:
                actions.append(
                    IncludeLaunchDescription(
                        PythonLaunchDescriptionSource(
                            os.path.join(pkg_rc_viz, 'launch', 'view_navigation.launch.py')
                        ),
                        launch_arguments={'use_sim_time': use_sim_time, 'namespace': '/rc'}.items(),
                    )
                )

        if moveit:
            actions.append(
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(
                        os.path.join(pkg_rc_manipulators, 'launch', 'moveit.launch.py')
                    ),
                    launch_arguments={'use_sim_time': use_sim_time}.items(),
                )
            )
            if rviz:
                actions.append(
                    IncludeLaunchDescription(
                        PythonLaunchDescriptionSource(
                            os.path.join(pkg_rc_viz, 'launch', 'view_moveit.launch.py')
                        ),
                        launch_arguments={'use_sim_time': use_sim_time, 'namespace': 'rc'}.items(),
                    )
                )

    return actions


def generate_launch_description():
    pkg_rc_nav2_demos = get_package_share_directory('rc_nav2_demos')
    default_map = os.path.join(pkg_rc_nav2_demos, 'maps', 'my_map.yaml')

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'mapping',
                default_value='false',
                choices=['true', 'false'],
                description='Launch mapping (SLAM) stack',
            ),
            DeclareLaunchArgument(
                'nav2',
                default_value='true',
                choices=['true', 'false'],
                description='Launch Nav2 navigation stack',
            ),
            DeclareLaunchArgument(
                'moveit',
                default_value='true',
                choices=['true', 'false'],
                description='Launch MoveIt arm control stack',
            ),
            DeclareLaunchArgument(
                'rviz',
                default_value='true',
                choices=['true', 'false'],
                description='Launch Rviz visualizers',
            ),
            DeclareLaunchArgument(
                'map', default_value=default_map, description='Path to the localization map file'
            ),
            DeclareLaunchArgument(
                'use_sim_time',
                default_value='true',
                choices=['true', 'false'],
                description='Use simulation clock',
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
