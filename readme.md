Autonomous UV-C Sterilization Robot

OVERVIEW
This repository contains a ROS 2 Humble package for an autonomous UV-C sterilization robot. Designed to operate in a warehouse/multi-room simulation, the robot utilizes LiDAR, AMCL localization, and the standard Nav2 stack to navigate and execute a predefined sterilization sequence.

FEATURES
- Custom URDF: Differential drive base integrated with a UV-C light payload and LiDAR/Odometry sensors.
- Autonomous Navigation: Real-time path planning using ROS 2 Nav2.
- Automated Tour Node: Python-based behavior script that interfaces with the NavigateToPose action server to sequence multi-room sterilization waypoints.
- Stable Visualization: Pre-configured launch profiles designed to bypass Ubuntu 22.04 OpenGL shader crashes in RViz2.

INSTALLATION & BUILD
Clone this repository into the src folder of your ROS 2 workspace:

cd ~/ros2_ws/src
git clone <YOUR_GITHUB_REPO_URL_HERE>
cd ~/ros2_ws
colcon build --packages-select sterilization_robot
source install/setup.bash

EXECUTION
To ensure system stability and prevent shader conflicts, run the following commands across four separate terminals.

1. Launch Simulation
Clears any corrupted ROS 2 shared memory and launches Gazebo and the Nav2 background nodes.

killall -9 rviz2 gazebo gzserver gzclient; pkill -f ros2; ros2 daemon stop; rm -rf /dev/shm/rtps* /dev/shm/fastrtps*
cd ~/ros2_ws
source install/setup.bash
ros2 launch sterilization_robot navigation.launch.py

2. Launch Safe RViz2
Forces CPU rendering overrides to prevent the indexed_8bit_image crash on Ubuntu 22.04.

cd ~/ros2_ws
source install/setup.bash
export MESA_GL_VERSION_OVERRIDE=3.3
export MESA_GLSL_VERSION_OVERRIDE=330
rviz2 -d /opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz --ros-args -p use_sim_time:=true

Note: In the RViz Displays panel, ensure RobotModel is checked. Uncheck Global Costmap and Local Costmap.

3. Inject Initial Pose
Synchronizes the Nav2 map with the robot's coordinates in Gazebo.

cd ~/ros2_ws
source install/setup.bash
ros2 topic pub -1 /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "{header: {frame_id: 'map'}, pose: {pose: {position: {x: -2.0, y: 1.0, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}}"

4. Start the Sterilization Tour
Executes the waypoint sequence.

cd ~/ros2_ws
source install/setup.bash
python3 src/sterilization_robot/sterilization_robot/sterilization_tour.py --ros-args -p use_sim_time:=true
