#!/usr/bin/env python3

import sys
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import tkinter as tk

class GUITeleop(Node):
    def __init__(self):
        super().__init__('gui_teleop')
        topic = '/omni_wheel_controller/cmd_vel_unstamped'
        self.publisher = self.create_publisher(Twist, topic, 10)
        self.get_logger().info(f'Publishing Twist to {topic}')
        
        self.linear_speed = 0.3
        self.angular_speed = 0.5
        self.speed_increment = 0.1

    def publish_twist(self, x, y, z):
        twist = Twist()
        twist.linear.x = x * self.linear_speed
        twist.linear.y = y * self.linear_speed
        twist.angular.z = z * self.angular_speed
        self.publisher.publish(twist)
        self.get_logger().info(f'Cmd: x={twist.linear.x:.2f}, y={twist.linear.y:.2f}, w={twist.angular.z:.2f}')

    def stop(self):
        twist = Twist()
        self.publisher.publish(twist)
        self.get_logger().info('STOP')


class TeleopApp:
    def __init__(self, root, node):
        self.root = root
        self.node = node
        self.root.title("Omni Robot Teleop")
        
        # UI Setup
        self.setup_ui()
        self.setup_bindings()
        
        # Periodic ROS spin
        self.timer = self.root.after(10, self.ros_spin)
        
        # Handle close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        # Frame for controls
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack()
        
        lbl = tk.Label(frame, text="Omni Robot GUI Control", font=("Arial", 16, "bold"))
        lbl.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Q W E
        btn_q = tk.Button(frame, text="↖ Q", width=5, height=2, command=lambda: self.move(0, 0, 1))
        btn_w = tk.Button(frame, text="↑ W", width=5, height=2, command=lambda: self.move(1, 0, 0))
        btn_e = tk.Button(frame, text="↗ E", width=5, height=2, command=lambda: self.move(0, 0, -1))
        
        # A S D
        btn_a = tk.Button(frame, text="← A", width=5, height=2, command=lambda: self.move(0, 1, 0))
        btn_s = tk.Button(frame, text="↓ S", width=5, height=2, command=lambda: self.move(-1, 0, 0))
        btn_d = tk.Button(frame, text="→ D", width=5, height=2, command=lambda: self.move(0, -1, 0))
        
        # Speed controls and Stop
        btn_minus = tk.Button(frame, text="-", width=5, height=2, command=self.decrease_speed)
        btn_stop = tk.Button(frame, text="STOP", width=5, height=2, bg="red", fg="white", command=self.stop)
        btn_plus = tk.Button(frame, text="+", width=5, height=2, command=self.increase_speed)
        
        btn_q.grid(row=1, column=0, padx=2, pady=2)
        btn_w.grid(row=1, column=1, padx=2, pady=2)
        btn_e.grid(row=1, column=2, padx=2, pady=2)
        
        btn_a.grid(row=2, column=0, padx=2, pady=2)
        btn_s.grid(row=2, column=1, padx=2, pady=2)
        btn_d.grid(row=2, column=2, padx=2, pady=2)
        
        btn_minus.grid(row=3, column=0, padx=2, pady=2)
        btn_stop.grid(row=3, column=1, padx=2, pady=2)
        btn_plus.grid(row=3, column=2, padx=2, pady=2)
        
        self.speed_lbl = tk.Label(frame, text=self.get_speed_text())
        self.speed_lbl.grid(row=4, column=0, columnspan=3, pady=(10, 0))

    def setup_bindings(self):
        self.root.bind('<w>', lambda e: self.move(1, 0, 0))
        self.root.bind('<s>', lambda e: self.move(-1, 0, 0))
        self.root.bind('<a>', lambda e: self.move(0, 1, 0))
        self.root.bind('<d>', lambda e: self.move(0, -1, 0))
        self.root.bind('<q>', lambda e: self.move(0, 0, 1))
        self.root.bind('<e>', lambda e: self.move(0, 0, -1))
        
        # Diagonals
        self.root.bind('<r>', lambda e: self.move(1, 1, 0))
        self.root.bind('<t>', lambda e: self.move(1, -1, 0))
        self.root.bind('<f>', lambda e: self.move(-1, 1, 0))
        self.root.bind('<g>', lambda e: self.move(-1, -1, 0))
        
        self.root.bind('<space>', lambda e: self.stop())
        self.root.bind('<plus>', lambda e: self.increase_speed())
        self.root.bind('<equal>', lambda e: self.increase_speed())
        self.root.bind('<minus>', lambda e: self.decrease_speed())
        
    def get_speed_text(self):
        return f"Linear: {self.node.linear_speed:.2f} m/s  |  Angular: {self.node.angular_speed:.2f} rad/s"

    def update_speed_lbl(self):
        self.speed_lbl.config(text=self.get_speed_text())

    def increase_speed(self):
        self.node.linear_speed += self.node.speed_increment
        self.node.angular_speed += self.node.speed_increment * 0.5
        self.update_speed_lbl()

    def decrease_speed(self):
        self.node.linear_speed = max(0.1, self.node.linear_speed - self.node.speed_increment)
        self.node.angular_speed = max(0.1, self.node.angular_speed - self.node.speed_increment * 0.5)
        self.update_speed_lbl()

    def move(self, x, y, z):
        self.node.publish_twist(x, y, z)

    def stop(self):
        self.node.stop()

    def ros_spin(self):
        if rclpy.ok():
            rclpy.spin_once(self.node, timeout_sec=0.01)
            self.timer = self.root.after(10, self.ros_spin)

    def on_close(self):
        self.stop()
        self.root.destroy()


def main(args=None):
    rclpy.init(args=args)
    node = GUITeleop()
    
    root = tk.Tk()
    app = TeleopApp(root, node)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
