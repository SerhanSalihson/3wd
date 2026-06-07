import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_path = get_package_share_directory('omni')
    quickstart_launch = os.path.join(
        package_path, 'launch', 'quickstart.launch.py'
    )
    map_output = LaunchConfiguration('map_output')

    complete_stack = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(quickstart_launch),
        launch_arguments={'navigation': 'true'}.items(),
    )
    explorer = TimerAction(
        period=18.0,
        actions=[
            Node(
                package='omni',
                executable='auto_mapper.py',
                name='auto_mapper',
                output='screen',
                parameters=[
                    {'use_sim_time': True},
                    {'map_output': map_output},
                ],
            )
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'map_output',
            default_value=os.path.expanduser('~/omni/maps/auto_map'),
            description='Output path without extension for the completed map.',
        ),
        complete_stack,
        explorer,
    ])
