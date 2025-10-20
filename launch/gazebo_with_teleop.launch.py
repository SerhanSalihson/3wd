import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    """
    Launch Gazebo simulation with keyboard teleop.
    
    NOTE: Requires 'xterm' to be installed for keyboard control.
    Install with: sudo apt install xterm
    
    If xterm is not available, run teleop manually in a separate terminal:
        ros2 run omni keyboard_teleop.py
    """

    # Package path
    pkg_path = get_package_share_directory('omni')
    
    # Include Gazebo launch
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_path, 'launch', 'gazebo.launch.py')
        )
    )

    # Keyboard Teleop Node (opens in xterm)
    keyboard_teleop = Node(
        package='omni',
        executable='keyboard_teleop.py',
        name='keyboard_teleop',
        output='screen',
        prefix='xterm -fa Monospace -fs 12 -e',  # Open in xterm window
    )

    return LaunchDescription([
        LogInfo(msg=[
            '\n',
            '='*60, '\n',
            'Launching Gazebo with Keyboard Teleop\n',
            'Note: Requires xterm (sudo apt install xterm)\n',
            '='*60
        ]),
        gazebo_launch,
        keyboard_teleop,
    ])
