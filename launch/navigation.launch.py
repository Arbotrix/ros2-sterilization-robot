import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_dir = get_package_share_directory('sterilization_robot')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    
    map_yaml_file = os.path.join(pkg_dir, 'maps', 'room_map.yaml')
    urdf_file = os.path.join(pkg_dir, 'urdf', 'robot.urdf')

    with open(urdf_file, 'r') as infp:
        robot_description_config = infp.read()

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(pkg_dir, 'launch', 'sim.launch.py'))
        ),
        
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'use_sim_time': True, 'robot_description': robot_description_config}]
        ),
        
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')),
            launch_arguments={'map': map_yaml_file, 'use_sim_time': 'true'}.items()
        )
    ])
