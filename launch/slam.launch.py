import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node


def generate_launch_description():
    pkg_path = get_package_share_directory('omni')
    slam_params = os.path.join(pkg_path, 'config', 'slam_toolbox.yaml')

    slam_toolbox = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_params, {'use_sim_time': True}],
    )

    configure_slam = TimerAction(
        period=2.0,
        actions=[
            ExecuteProcess(
                cmd=['ros2', 'lifecycle', 'set', '/slam_toolbox', 'configure'],
                output='screen',
            )
        ],
    )

    activate_slam = TimerAction(
        period=4.0,
        actions=[
            ExecuteProcess(
                cmd=['ros2', 'lifecycle', 'set', '/slam_toolbox', 'activate'],
                output='screen',
            )
        ],
    )

    return LaunchDescription([slam_toolbox, configure_slam, activate_slam])
