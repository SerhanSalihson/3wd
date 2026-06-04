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

                                             irrrrrri
                                    rrsAAXXAXr;
                                   riXrA2sX3srir;
                                X2irsArh5r5hrsrrXr;
                             is2AAsissXsrssrriirXri
                             sX3AsXrrXXrrssssriiii
                              sA2AsisXAXX222Asririi
                                rsAA2AXAXAAXsriAS3r
                               irh#SSGA25XX2sXXA2Xi
                                sXAAX5225s2AXXrrri               rX  s
                                 rsssssXXsXssssr                s5h 2Xss
                                      223352X                  Xr35iXsX2
                                     ,irXAXsr;                 XAAsrX3M
                         ,,::;:XHMGMHA;rsA2si:3MMh              rX2MHS
                     ,,,:,,:;:iMSGGGHSMX3SG5XGSHSGHM5;;;::     XAr5
                  ,,,,,,:;iiisH###SSSSSHGGGHGSS#SSSGGs;;:::;i;;sXrs:
                ,,,,;;iirrrrXH###S#SS#SS#SSSSSSSSSSS#hiiiirAM2sXXXrrii
               ,,;irrrssssA2H##SSS#####SS#SSS###S#GSSGsiirA3M5XXXXAAsi
              ,,irssssA2223MSSS#SS#S#S########SSSSSGS#3riiirssssssssi;
             ,,;rXAA23hh53MHGS###############SS#S#SSS#SAii;;rsXAA22As:,
             ,,;rsXA533Xr  HGGSS###S##################BMr;rrsXsssssrs::
             ::irsXA252i;  GHHSS###########9#9##9#99999BXrrrrsAA22Xsrr::
             ::irsXAA5M5  hHHSS######9#9#99#9#9999999B#5:srX2AXXssXXsii
             :;irsAA53MM  MMGSS########999999999BBBBBGsrssss5h2522AXsr
             :;irXXA3MMM  HGSSS###9#9####999999B9BB9BhiMSAXsXAA5552
            ,,;rsXXX5MMh  #GHS####99999999999BBBBB99ShAM3 X5h
            ,.;irsXA5MHM  #SS#999999999999999999999#Gh52
            :rXXXA25MHSG  999999999999999999999999#SGM5A
            ;irirsA23HG   9999999999999############SHh5A
            ,,::iXXXA2hM  99999999999999999#########Hh52
           :,;;;sX5HG35M  B999999BBBBBB99BB99######SHh5A
          A;irsrXAM#MhhH#SBB9BB9BBBBBBS  9999######SH35A
          #HXsA525332hHMSSB&B&BBBBBBBS3   99#######SSh2A
        hhMGGMMGGHMMhHGGSSB&&&&BBBBB#M5   99######SSG322
3hHHHGSSSSSSSSSGGHSB99#SSS9BBBBBB&&B#H3   99########Sh2A
MMMMMMHHGG#9#SSSS#9B&&9SS#9#####B&BB9Sh   99########SM5A
 HSSSGGGGS####99##9#9&#SS9B99B9#B&BB9Gh   99########SM32
 HSGGGGGSGS##99999S#B&#S##99####BBBB9Gh5  #9########SM35
 SSSSSSSSSS#999999999B##9B9#99##BBBB9#Gh5 99########GMh
 HHGGGGSSSS99999#999BB##9#99##99BBBB99SH3M999#######GMh
 HHGGGGHGHGS##9999#9&9S#9999B99#BBBBB9SGHS99#######GHM3
 HHGGGGHHHHS###9999BB9S#99999B99BBBB99#SHS99######SHMh5
 HHGHHHHHHHS#999999999##9#######9BBBB#SGG##########SHh5
    HHHHHHHGSS##99999#####999#S#9#Gh33MG #########GMMh2
           HSSS###        #9BBBBB9SHMHG  ####9999#SHM32
                          G#B&BBBB9#GH  ####999999#GGM2
                                        ##99999#9999#G352
                                        9BB99999999999#Hh
                                         999999999999999S
                                          BBBBBBBBBBB999


        Made with no love whatsoever by Serhan S.
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
