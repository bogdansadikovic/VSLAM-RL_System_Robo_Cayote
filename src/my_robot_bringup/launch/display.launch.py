import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('my_robot_bringup')
    
    # Paths to your config files
    urdf_file = os.path.join(pkg_share, 'urdf', 'robo_cayote.urdf')
    ekf_config_path = os.path.join(pkg_share, 'config', 'ekf.yaml')
    costmap_config_path = os.path.join(pkg_share, 'config', 'costmap.yaml')
    
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    return LaunchDescription([
        # Node 1: Broadcasts the robot's fixed physical layout
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_desc}]
        ),
        
        # Node 2: Dummy "0" angles for the wheels
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_desc,
                'use_sim_time': False,
            }]
        ),
        
        # Node 3: The Extended Kalman Filter
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[ekf_config_path]
        ),
        
        # Node 5: Nav2 Controller Server (The Standard Way)
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[costmap_config_path]
        ),
        
        # Node 6: The Lifecycle Manager
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[
                {'use_sim_time': False},
                {'autostart': True},
                {'node_names': ['controller_server']} # Managing the controller now
            ]
        )
    ])