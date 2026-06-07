import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro


def generate_launch_description():

    # Package Directories
    pkg_path = get_package_share_directory('omni')
    
    # Paths
    xacro_file = os.path.join(pkg_path, 'description', 'robot.urdf.xacro')
    world_file = os.path.join(pkg_path, 'worlds', 'obstacles.sdf')
    
    # Process the URDF
    robot_description_config = xacro.process_file(
        xacro_file,
        mappings={'use_sim': 'true'}
    )
    robot_description = {'robot_description': robot_description_config.toxml()}

    # Gazebo Sim (Ignition) launch with GUI
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={
            'gz_args': f'-r {world_file}'
        }.items()
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': True}]
    )

    # Spawn robot in Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description',
                   '-name', 'omni_robot',
                   '-x', '-1.35',
                   '-y', '0.35',
                   '-z', '0.1'],
        output='screen'
    )

    # Bridge for clock
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )

    scan_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'],
        output='screen'
    )

    scan_frame_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=[
            '--x', '0',
            '--y', '0',
            '--z', '0.108',
            '--roll', '0',
            '--pitch', '0',
            '--yaw', '0',
            '--frame-id', 'base_link',
            '--child-frame-id', 'omni_robot/base_link/lidar',
        ],
        output='screen',
    )

    joint_state_broadcaster_spawner = TimerAction(
        period=3.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=[
                    'joint_state_broadcaster',
                    '--controller-manager',
                    '/controller_manager',
                ],
                output='screen',
            )
        ],
    )

    omni_controller_spawner = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=[
                    'omni_wheel_controller',
                    '--controller-manager',
                    '/controller_manager',
                ],
                output='screen',
            )
        ],
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        clock_bridge,
        scan_bridge,
        scan_frame_tf,
        spawn_entity,
        joint_state_broadcaster_spawner,
        omni_controller_spawner,
    ])
