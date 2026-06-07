#!/usr/bin/env python3

import sys
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
                'ERROR: Not running in a terminal! '
                'Please run: ros2 run omni keyboard_teleop.py'
            )
            raise RuntimeError('Not running in a terminal (TTY required)')
        
        # Simple Twist publisher
        topic = '/omni_wheel_controller/cmd_vel_unstamped'
        self.publisher = self.create_publisher(Twist, topic, 10)
        self.get_logger().info(f'Publishing Twist to {topic}')
        
        # Movement parameters
        self.linear_speed = 0.3  # m/s
        self.angular_speed = 0.5  # rad/s
        self.speed_increment = 0.1
        
        # Key mappings
        self.key_bindings = {
            'w': (1, 0, 0),   # Forward
            's': (-1, 0, 0),  # Backward
            'a': (0, 1, 0),   # Left (strafe)
            'd': (0, -1, 0),  # Right (strafe)
            'q': (0, 0, 1),   # Rotate counter-clockwise
            'e': (0, 0, -1),  # Rotate clockwise
            # Diagonal combinations (omnidirectional)
            'r': (1, 1, 0),   # Forward-Left diagonal
            't': (1, -1, 0),  # Forward-Right diagonal
            'f': (-1, 1, 0),  # Backward-Left diagonal
            'g': (-1, -1, 0), # Backward-Right diagonal
        }
        
        self.print_instructions()

    def print_instructions(self):
        msg = """
OMNI ROBOT KEYBOARD CONTROL

Movement:
  W/S: forward/backward
  A/D: strafe left/right
  Q/E: rotate left/right

Diagonals:
  R/T: forward-left / forward-right
  F/G: backward-left / backward-right

Other:
  +/-: adjust speed
  SPACE: stop
  ESC or Ctrl+C: quit

Current speed - linear: {:.2f} m/s, angular: {:.2f} rad/s
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
        self.get_logger().info(f'Cmd: x={twist.linear.x:.2f}, y={twist.linear.y:.2f}, w={twist.angular.z:.2f}')

    def stop(self):
        """Stop the robot."""
        if not self.context.ok():
            return
        twist = Twist()
        try:
            self.publisher.publish(twist)
            self.get_logger().info('STOP')
        except Exception:
            pass

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
                        f'Speed UP - Linear: {self.linear_speed:.2f} m/s, '
                        f'Angular: {self.angular_speed:.2f} rad/s'
                    )
                elif key == '-' or key == '_':
                    self.linear_speed = max(0.1, self.linear_speed - self.speed_increment)
                    self.angular_speed = max(0.1, self.angular_speed - self.speed_increment * 0.5)
                    self.get_logger().info(
                        f'Speed DOWN - Linear: {self.linear_speed:.2f} m/s, '
                        f'Angular: {self.angular_speed:.2f} rad/s'
                    )
                
                # Movement
                elif key in self.key_bindings:
                    x, y, z = self.key_bindings[key]
                    self.publish_twist(x, y, z)
        
        except Exception as e:
            self.get_logger().error(f'Error: {str(e)}')
        
        finally:
            self.stop()


def main(args=None):
    rclpy.init(args=args)
    node = KeyboardTeleop()

    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
