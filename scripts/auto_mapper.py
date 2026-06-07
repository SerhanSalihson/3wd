#!/usr/bin/env python3

import math
import os
import subprocess
from collections import deque

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import OccupancyGrid
from rclpy.action import ActionClient
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from rclpy.time import Time
from tf2_ros import Buffer, TransformException, TransformListener


class AutoMapper(Node):
    """Explore occupancy-grid frontiers with Nav2 and save the completed map."""

    def __init__(self):
        super().__init__('auto_mapper')
        self.declare_parameter('map_output', '~/omni/maps/auto_map')
        self.declare_parameter('minimum_frontier_cells', 8)
        self.declare_parameter('goal_blacklist_radius', 0.65)
        self.declare_parameter('completion_checks', 5)

        self.map_output = os.path.expanduser(
            self.get_parameter('map_output').get_parameter_value().string_value
        )
        self.minimum_frontier_cells = self.get_parameter(
            'minimum_frontier_cells'
        ).get_parameter_value().integer_value
        self.blacklist_radius = self.get_parameter(
            'goal_blacklist_radius'
        ).get_parameter_value().double_value
        self.completion_checks = self.get_parameter(
            'completion_checks'
        ).get_parameter_value().integer_value

        map_qos = QoSProfile(depth=1)
        map_qos.reliability = ReliabilityPolicy.RELIABLE
        map_qos.durability = DurabilityPolicy.TRANSIENT_LOCAL
        self.map_subscription = self.create_subscription(
            OccupancyGrid, '/map', self._map_callback, map_qos
        )
        self.navigator = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.timer = self.create_timer(2.0, self._explore)

        self.map = None
        self.goal_active = False
        self.current_target = None
        self.visited_targets = []
        self.empty_frontier_checks = 0
        self.map_saved = False
        self.mapping_finished = False
        self.get_logger().info(
            'Battery loaded: auto mapping is waiting for SLAM and Nav2...'
        )

    def _map_callback(self, msg):
        self.map = msg

    def _robot_pose(self):
        try:
            transform = self.tf_buffer.lookup_transform(
                'map', 'base_link', Time(), timeout=Duration(seconds=0.2)
            )
        except TransformException as error:
            self.get_logger().debug(f'Waiting for map -> base_link: {error}')
            return None
        translation = transform.transform.translation
        rotation = transform.transform.rotation
        yaw = math.atan2(
            2.0 * (rotation.w * rotation.z + rotation.x * rotation.y),
            1.0 - 2.0 * (rotation.y ** 2 + rotation.z ** 2),
        )
        return translation.x, translation.y, yaw

    @staticmethod
    def _neighbors(index, width, height, diagonals=False):
        x = index % width
        y = index // width
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if diagonals:
            offsets += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in offsets:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                yield ny * width + nx

    def _frontier_clusters(self):
        info = self.map.info
        data = self.map.data
        width, height = info.width, info.height
        frontier = set()

        for index, value in enumerate(data):
            if 0 <= value <= 20 and any(
                data[n] == -1 for n in self._neighbors(index, width, height)
            ):
                frontier.add(index)

        clusters = []
        while frontier:
            seed = frontier.pop()
            cluster = [seed]
            queue = deque([seed])
            while queue:
                current = queue.popleft()
                for neighbor in self._neighbors(
                    current, width, height, diagonals=True
                ):
                    if neighbor in frontier:
                        frontier.remove(neighbor)
                        cluster.append(neighbor)
                        queue.append(neighbor)
            if len(cluster) >= self.minimum_frontier_cells:
                clusters.append(cluster)
        return clusters

    def _cell_to_world(self, index):
        info = self.map.info
        cell_x = index % info.width
        cell_y = index // info.width
        local_x = (cell_x + 0.5) * info.resolution
        local_y = (cell_y + 0.5) * info.resolution
        orientation = info.origin.orientation
        yaw = math.atan2(
            2.0 * (orientation.w * orientation.z + orientation.x * orientation.y),
            1.0 - 2.0 * (orientation.y ** 2 + orientation.z ** 2),
        )
        cosine, sine = math.cos(yaw), math.sin(yaw)
        return (
            info.origin.position.x + cosine * local_x - sine * local_y,
            info.origin.position.y + sine * local_x + cosine * local_y,
        )

    def _has_clearance(self, index):
        info = self.map.info
        radius = max(1, math.ceil(0.20 / info.resolution))
        x, y = index % info.width, index // info.width
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < info.width and 0 <= ny < info.height):
                    return False
                if self.map.data[ny * info.width + nx] > 50:
                    return False
        return True

    def _select_target(self, robot):
        candidates = []
        for cluster in self._frontier_clusters():
            clear_cells = [cell for cell in cluster if self._has_clearance(cell)]
            if not clear_cells:
                continue
            center_x = sum(cell % self.map.info.width for cell in clear_cells) / len(clear_cells)
            center_y = sum(cell // self.map.info.width for cell in clear_cells) / len(clear_cells)
            cell = min(
                clear_cells,
                key=lambda item: (
                    (item % self.map.info.width - center_x) ** 2
                    + (item // self.map.info.width - center_y) ** 2
                ),
            )
            target = self._cell_to_world(cell)
            distance = math.hypot(target[0] - robot[0], target[1] - robot[1])
            if distance < 0.45:
                continue
            if any(
                math.hypot(target[0] - old[0], target[1] - old[1])
                < self.blacklist_radius
                for old in self.visited_targets
            ):
                continue
            score = len(cluster) * self.map.info.resolution - 0.35 * distance
            candidates.append((score, target, len(cluster)))
        return max(candidates, default=None, key=lambda item: item[0])

    def _explore(self):
        if self.map_saved or self.goal_active or self.map is None:
            return
        if not self.navigator.wait_for_server(timeout_sec=0.1):
            return
        robot = self._robot_pose()
        if robot is None:
            return

        selected = self._select_target(robot[:2])
        if selected is None:
            self.empty_frontier_checks += 1
            if self.empty_frontier_checks >= self.completion_checks:
                self._save_map()
            else:
                self.get_logger().info(
                    'No leaf-clover frontier found; checking again '
                    f'({self.empty_frontier_checks}/{self.completion_checks})'
                )
            return

        self.empty_frontier_checks = 0
        _, target, cluster_size = selected
        target_yaw = math.atan2(target[1] - robot[1], target[0] - robot[0])

        self.current_target = target
        self.goal_active = True
        self.get_logger().info(
            f'Seek and explore frontier at ({target[0]:.2f}, {target[1]:.2f}), '
            f'{cluster_size} cells'
        )
        self._send_goal(target[0], target[1], target_yaw)

    def _send_goal(self, x, y, yaw):
        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal.pose.pose.orientation.w = math.cos(yaw / 2.0)
        future = self.navigator.send_goal_async(goal)
        future.add_done_callback(self._goal_response)

    def _goal_response(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warning(
                'Nav2 rejected the frontier goal. Sad but true.'
            )
            self._finish_goal()
            return
        result = goal_handle.get_result_async()
        result.add_done_callback(self._goal_result)

    def _goal_result(self, future):
        status = future.result().status
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(
                'Frontier reached; roaming where the wild frontiers are next'
            )
        else:
            self.get_logger().warning(
                f'Frontier navigation ended with status {status}; skipping it'
            )
        self._finish_goal()

    def _finish_goal(self):
        if self.current_target is not None:
            self.visited_targets.append(self.current_target)
        self.current_target = None
        self.goal_active = False

    def _save_map(self):
        self.map_saved = True
        output_directory = os.path.dirname(self.map_output) or '.'
        os.makedirs(output_directory, exist_ok=True)
        self.get_logger().info(
            f'Ride the Lightning: saving map to {self.map_output}.yaml'
        )
        try:
            subprocess.run(
                [
                    'ros2', 'run', 'nav2_map_server', 'map_saver_cli',
                    '-f', self.map_output,
                    '--ros-args', '-p', 'save_map_timeout:=10000.0',
                ],
                check=True,
                timeout=30,
            )
            self.mapping_finished = True
            self.timer.cancel()
            self.get_logger().info(
                f'Nothing else matters - map saved to {self.map_output}.yaml'
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
            self.map_saved = False
            self.empty_frontier_checks = 0
            self.get_logger().error(f'The map that failed should not be: {error}')


def main(args=None):
    rclpy.init(args=args)
    node = AutoMapper()
    try:
        while rclpy.ok() and not node.mapping_finished:
            rclpy.spin_once(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
