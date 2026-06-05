import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    LogInfo,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    navigation_enabled = LaunchConfiguration("navigation")
    pkg_path = get_package_share_directory('omni')
    gazebo_launch = os.path.join(pkg_path, 'launch', 'gazebo.launch.py')
    rviz_config = os.path.join(pkg_path, 'rviz', 'omni_quickstart.rviz')
    slam_launch = os.path.join(pkg_path, 'launch', 'slam.launch.py')
    navigation_launch = os.path.join(pkg_path, 'launch', 'navigation.launch.py')
    art_path = os.path.join(pkg_path, 'config', 'ride_the_lightning.txt')
    with open(art_path, encoding='ascii') as art_file:
        splash = art_file.read()

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch)
    )

    slam = TimerAction(
        period=6.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(slam_launch)
            )
        ],
    )

    navigation = TimerAction(
        period=12.0,
        condition=IfCondition(navigation_enabled),
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(navigation_launch)
            )
        ],
    )

    rviz = ExecuteProcess(
        cmd=[
            "bash",
            "-c",
            "until timeout 5 ros2 topic echo /map --once "
            "--qos-durability transient_local >/dev/null 2>&1; do "
            "sleep 0.2; done; "
            "exec ros2 run rviz2 rviz2 -d \"$1\" "
            "--ros-args -p use_sim_time:=true",
            "bash",
            rviz_config,
        ],
        output="screen",
    )


    return LaunchDescription([
        DeclareLaunchArgument(
            "navigation",
            default_value="true",
            description="Start Nav2. Set false for SLAM-only mapping mode.",
        ),
        LogInfo(msg=[
            '\n',
            splash,
            'Starting Omni: Gazebo + SLAM Toolbox + RViz\n',
            'Navigation mode: use the Nav2 Goal tool. Mapping mode: drive manually.\n',
        ]),
        gazebo,
        slam,
        navigation,
        rviz,
    ])
