import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_dir = get_package_share_directory('sterilization_robot')
    slam_dir = get_package_share_directory('slam_toolbox')

    return LaunchDescription([
        # 1. Launch our existing Gazebo simulation
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(pkg_dir, 'launch', 'sim.launch.py'))
        ),
        
        # 2. Launch SLAM Toolbox for mapping
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(slam_dir, 'launch', 'online_async_launch.py')),
            launch_arguments={'use_sim_time': 'true'}.items()
        ),
        
        # 3. Launch RViz2
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            parameters=[{'use_sim_time': True}]
        )
    ])
