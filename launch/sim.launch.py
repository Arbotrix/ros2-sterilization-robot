import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_dir = get_package_share_directory('sterilization_robot')
    urdf_file = os.path.join(pkg_dir, 'urdf', 'robot.urdf')
    world_file = os.path.join(pkg_dir, 'worlds', 'two_rooms.world')

    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    return LaunchDescription([
        # Prevent the Wayland crashing bug we debugged earlier
        SetEnvironmentVariable('QT_QPA_PLATFORM', 'xcb'), 
        
        # Open Gazebo with our 2-room world
        ExecuteProcess(
            cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_init.so', '-s', 'libgazebo_ros_factory.so', world_file],
            output='screen'
        ),
        
        # Publish the robot's transforms (wheels, LiDAR, base)
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
        ),
        
        # Spawn the UV Robot into the world
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=['-entity', 'uv_robot', '-topic', 'robot_description', '-x', '-2.0', '-y', '1.0', '-z', '0.1'],
            output='screen'
        )
    ])
