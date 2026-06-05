import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, LogInfo, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
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
        period=10.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(navigation_launch)
            )
        ],
    )

    rviz = TimerAction(
        period=2.0,
        actions=[
            Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2',
                arguments=['-d', rviz_config],
                parameters=[{'use_sim_time': True}],
                output='screen',
            )
        ],
    )


    return LaunchDescription([
        LogInfo(msg=[
            '\n',
            splash,
            'Starting Omni navigation: Gazebo + SLAM Toolbox + Nav2 + RViz\n',
            'Use the Nav2 Goal tool in RViz to click and drag a destination.\n',
        ]),
        gazebo,
        slam,
        navigation,
        rviz,
    ])
