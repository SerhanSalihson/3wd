from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import LogInfo


def generate_launch_description():
    """
    Launch keyboard teleop node for omni robot control.
    
    NOTE: This launch file may not work properly because keyboard input
    requires a real TTY terminal. 
    
    RECOMMENDED: Run the teleop node directly in a terminal instead:
        ros2 run omni keyboard_teleop.py
    """
    
    return LaunchDescription([
        LogInfo(msg=[
            '\n',
            '='*60, '\n',
            'WARNING: Keyboard teleop may not work via launch file!\n',
            'If you see errors, run directly in a terminal:\n',
            '  ros2 run omni keyboard_teleop.py\n',
            '='*60
        ]),
        Node(
            package='omni',
            executable='keyboard_teleop.py',
            name='keyboard_teleop',
            output='screen',
            prefix='xterm -e',  # Try to open in xterm
        )
    ])
