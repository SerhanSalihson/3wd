#!/usr/bin/env python3

import sys
import threading
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

# For Linux
try:
    import termios
    import tty
except ImportError:
    termios = None
    tty = None

class KeyboardTeleop(Node):
    def __init__(self):
        super().__init__('keyboard_teleop')
        
        # Check if running in a proper terminal
        if not sys.stdin.isatty():
            self.get_logger().error(
                '='*60 + '\n' +
                'ERROR: Not running in a terminal!\n' +
                'This node requires a TTY for keyboard input.\n\n' +
                'Please run directly in a terminal:\n' +
                '  ros2 run omni keyboard_teleop.py\n\n' +
                'Or in a separate terminal window, not via launch file.\n' +
                '='*60
            )
            raise RuntimeError('Not running in a terminal (TTY required)')
        
        # Publisher
        self.publisher = self.create_publisher(
            Twist, 
            '/omni_wheel_controller/cmd_vel', 
            10
        )
        
        # Movement parameters
        self.linear_speed = 0.3  # m/s
        self.angular_speed = 0.5  # rad/s
        self.speed_increment = 0.1
        
        # Key mappings
        self.key_bindings = {
            'w': (1, 0, 0),   # Forward
            's': (-1, 0, 0),  # Backward
            'a': (0, 1, 0),   # Left
            'd': (0, -1, 0),  # Right
            'q': (0, 0, 1),   # Rotate counter-clockwise
            'e': (0, 0, -1),  # Rotate clockwise
            # Diagonal movements
            'r': (1, 1, 0),   # Forward-left
            't': (1, -1, 0),  # Forward-right
            'f': (-1, 1, 0),  # Backward-left
            'g': (-1, -1, 0), # Backward-right
        }
        
        self.get_logger().info('Keyboard Teleop Node Started!')
        self.print_instructions()

    def print_instructions(self):
        msg = """
        ╔═══════════════════════════════════════╗
        ║   OMNI ROBOT KEYBOARD CONTROL         ║
        ╠═══════════════════════════════════════╣
        ║                                       ║
        ║   Movement Controls:                  ║
        ║   ─────────────────                   ║
        ║      W : Forward                      ║
        ║      S : Backward                     ║
        ║      A : Strafe Left                  ║
        ║      D : Strafe Right                 ║
        ║      Q : Rotate Left (CCW)            ║
        ║      E : Rotate Right (CW)            ║
        ║                                       ║
        ║   Diagonal Movement:                  ║
        ║   ─────────────────                   ║
        ║      R : Forward-Left                 ║
        ║      T : Forward-Right                ║
        ║      F : Backward-Left                ║
        ║      G : Backward-Right               ║
        ║                                       ║
        ║   Speed Control:                      ║
        ║   ─────────────                       ║
        ║      + : Increase speed               ║
        ║      - : Decrease speed               ║
        ║                                       ║
        ║   Other:                              ║
        ║   ─────                               ║
        ║   SPACE : Stop                        ║
        ║   ESC/Ctrl+C : Quit                   ║
        ║                                       ║
        ╚═══════════════════════════════════════╝
        
        Current Speed - Linear: {:.2f} m/s, Angular: {:.2f} rad/s
        """.format(self.linear_speed, self.angular_speed)
        print(msg)

    def get_key(self):
        """Get a single keypress from the terminal."""
        if termios is None:
            # Windows fallback
            try:
                import msvcrt
                return msvcrt.getch().decode('utf-8').lower()
            except ImportError:
                # Not Windows and no termios - use input
                return input().lower()[:1] if input() else ' '
        else:
            # Linux/Mac
            try:
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    ch = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                return ch.lower()
            except (termios.error, OSError) as e:
                # Not a TTY - not running in proper terminal
                self.get_logger().error(
                    'This node must be run in a terminal (TTY). '
                    'Try: ros2 run omni keyboard_teleop.py'
                )
                raise RuntimeError(
                    'Not running in a terminal. Cannot read keyboard input.'
                ) from e

    def publish_twist(self, x, y, z):
        """Publish velocity command."""
        twist = Twist()
        twist.linear.x = x * self.linear_speed
        twist.linear.y = y * self.linear_speed
        twist.angular.z = z * self.angular_speed
        self.publisher.publish(twist)

    def stop(self):
        """Stop the robot."""
        twist = Twist()
        self.publisher.publish(twist)
        self.get_logger().info('Robot stopped')

    def run(self):
        """Main loop for keyboard control."""
        try:
            while rclpy.ok():
                key = self.get_key()
                
                # Check for escape or quit
                if key == '\x1b' or key == '\x03':  # ESC or Ctrl+C
                    self.get_logger().info('Shutting down...')
                    break
                
                # Stop
                elif key == ' ':
                    self.stop()
                
                # Speed control
                elif key == '+' or key == '=':
                    self.linear_speed += self.speed_increment
                    self.angular_speed += self.speed_increment * 0.5
                    self.get_logger().info(
                        f'Speed increased - Linear: {self.linear_speed:.2f} m/s, '
                        f'Angular: {self.angular_speed:.2f} rad/s'
                    )
                elif key == '-' or key == '_':
                    self.linear_speed = max(0.1, self.linear_speed - self.speed_increment)
                    self.angular_speed = max(0.1, self.angular_speed - self.speed_increment * 0.5)
                    self.get_logger().info(
                        f'Speed decreased - Linear: {self.linear_speed:.2f} m/s, '
                        f'Angular: {self.angular_speed:.2f} rad/s'
                    )
                
                # Movement
                elif key in self.key_bindings:
                    x, y, z = self.key_bindings[key]
                    self.publish_twist(x, y, z)
                    direction = {
                        'w': 'Forward', 's': 'Backward', 
                        'a': 'Left', 'd': 'Right',
                        'q': 'Rotate Left', 'e': 'Rotate Right',
                        'r': 'Forward-Left', 't': 'Forward-Right',
                        'f': 'Backward-Left', 'g': 'Backward-Right'
                    }
                    self.get_logger().info(f'Moving: {direction.get(key, "Unknown")}')
                
                # Unknown key
                else:
                    if key.isprintable():
                        self.get_logger().warn(f'Unknown key: {key}')
        
        except Exception as e:
            self.get_logger().error(f'Error: {str(e)}')
        
        finally:
            self.stop()


def main(args=None):
    rclpy.init(args=args)
    
    node = KeyboardTeleop()
    
    # Run in a separate thread to allow ROS to spin
    teleop_thread = threading.Thread(target=node.run, daemon=True)
    teleop_thread.start()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
