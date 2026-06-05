import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():
    pkg_path = get_package_share_directory("omni")
    slam_params = os.path.join(pkg_path, "config", "slam_toolbox.yaml")

    slam_toolbox = Node(
        package="slam_toolbox",
        executable="async_slam_toolbox_node",
        name="slam_toolbox",
        output="screen",
        parameters=[slam_params, {"use_sim_time": True}],
    )

    activate_slam = ExecuteProcess(
        cmd=[
            "bash",
            "-c",
            "until ros2 lifecycle get /slam_toolbox >/dev/null 2>&1; do "
            "sleep 0.2; done; "
            "ros2 lifecycle set /slam_toolbox configure && "
            "ros2 lifecycle set /slam_toolbox activate",
        ],
        output="screen",
    )

    return LaunchDescription([slam_toolbox, activate_slam])
