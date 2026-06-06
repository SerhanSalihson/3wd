#!/usr/bin/env python3

"""
Codebase of doom and despair.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import time


class RobotTester(Node):
    def __init__(self):
        super().__init__('robot_tester')
        
        # Publisher for velocity commands
        self.cmd_pub = self.create_publisher(
            Twist,
            '/omni_wheel_controller/cmd_vel_unstamped',
            10
        )
        
        # Subscriber for odometry feedback
        self.odom_sub = self.create_subscription(
            Odometry,
            '/omni_wheel_controller/odom',
            self.odom_callback,
            10
        )
        
        self.last_odom = None
        self.get_logger().info('Robot Tester Started!')
        
    def odom_callback(self, msg):
        self.last_odom = msg
        
    def send_velocity(self, vx, vy, wz, duration=2.0):
        """Send velocity command for specified duration."""
        twist = Twist()
        twist.linear.x = vx
        twist.linear.y = vy
        twist.angular.z = wz
        
        self.get_logger().info(
            f'Sending: vx={vx:.2f}, vy={vy:.2f}, wz={wz:.2f} for {duration}s'
        )
        
        start_time = time.time()
        rate = self.create_rate(20)  # 20 Hz
        
        while (time.time() - start_time) < duration and rclpy.ok():
            self.cmd_pub.publish(twist)
            rclpy.spin_once(self, timeout_sec=0.05)
            rate.sleep()
        
        # Stop
        twist.linear.x = 0.0
        twist.linear.y = 0.0
        twist.angular.z = 0.0
        self.cmd_pub.publish(twist)
        
        if self.last_odom:
            self.get_logger().info(
                f'Odom feedback - '
                f'x: {self.last_odom.twist.twist.linear.x:.3f}, '
                f'y: {self.last_odom.twist.twist.linear.y:.3f}, '
                f'θ: {self.last_odom.twist.twist.angular.z:.3f}'
            )
        else:
            self.get_logger().warn('No odometry feedback received!')
            
    def run_tests(self):
        """Run a series of movement tests."""
        self.get_logger().info('='*60)
        self.get_logger().info('Starting Robot Movement Tests')
        self.get_logger().info('='*60)
        
        # Wait for odometry
        self.get_logger().info('Waiting for odometry feedback...')
        timeout = 10.0
        start = time.time()
        while self.last_odom is None and (time.time() - start) < timeout:
            rclpy.spin_once(self, timeout_sec=0.1)
        
        if self.last_odom is None:
            self.get_logger().error('No odometry received! Controller may not be running.')
            return False
        
        self.get_logger().info('✓ Odometry OK')
        time.sleep(1)
        
        # Test 1: Forward
        self.get_logger().info('\n[Test 1] Moving Forward')
        self.send_velocity(0.2, 0.0, 0.0, 2.0)
        time.sleep(1)
        
        # Test 2: Backward
        self.get_logger().info('\n[Test 2] Moving Backward')
        self.send_velocity(-0.2, 0.0, 0.0, 2.0)
        time.sleep(1)
        
        # Test 3: Strafe Left
        self.get_logger().info('\n[Test 3] Strafing Left')
        self.send_velocity(0.0, 0.2, 0.0, 2.0)
        time.sleep(1)
        
        # Test 4: Strafe Right
        self.get_logger().info('\n[Test 4] Strafing Right')
        self.send_velocity(0.0, -0.2, 0.0, 2.0)
        time.sleep(1)
        
        # Test 5: Rotate CCW
        self.get_logger().info('\n[Test 5] Rotating Counter-Clockwise')
        self.send_velocity(0.0, 0.0, 0.5, 2.0)
        time.sleep(1)
        
        # Test 6: Rotate CW
        self.get_logger().info('\n[Test 6] Rotating Clockwise')
        self.send_velocity(0.0, 0.0, -0.5, 2.0)
        time.sleep(1)
        
        self.get_logger().info('\n' + '='*60)
        self.get_logger().info('All tests complete!')
        self.get_logger().info('='*60)
        
        return True


def main(args=None):
    rclpy.init(args=args)
    
    tester = RobotTester()
    
    try:
        success = tester.run_tests()
        if not success:
            tester.get_logger().error('Tests failed!')
    except KeyboardInterrupt:
        pass
    finally:
        tester.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
