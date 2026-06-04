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

    teleop = TimerAction(
        period=7.0,
        actions=[
            Node(
                package='omni',
                executable='keyboard_teleop.py',
                name='keyboard_teleop',
                prefix='xterm -fa Monospace -fs 12 -T "Omni Teleop" -e',
                output='screen',
            )
        ],
    )

    return LaunchDescription([
        LogInfo(msg=[
            '\n',
            'Starting Omni quickstart: Gazebo + RViz + SLAM Toolbox + keyboard teleop\n',
            'Teleop opens in an xterm window. Use W/A/S/D, Q/E, SPACE, ESC.\n',
        ]),
        gazebo,
        slam,
        rviz,
        teleop,
    ])
