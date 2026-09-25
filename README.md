# Autonomous UV-C Sterilization Robot

Autonomous UV-C sterilization robot with a differential-drive base, built on **ROS 2 Humble** and the **Nav2** navigation stack, simulated in **Gazebo Classic** and visualized in **RViz2**.

Repository: `github.com/Arbotrix/ros2-sterilization-robot`

## System Overview

| Component | Detail |
|---|---|
| Robot platform | Differential drive base |
| Sensors | LiDAR (`base_scan`) + wheel odometry |
| OS / Simulator | Ubuntu 22.04, Gazebo Classic |
| Middleware | ROS 2 Humble |
| Navigation | Nav2 — AMCL localization + `NavigateToPose` waypoint sequencing |
| Visualization | RViz2 |
| Workspace | `~/ros2_ws` |
| Package | `sterilization_robot` |

## Prerequisites

- Ubuntu 22.04
- ROS 2 Humble (with Nav2 and Gazebo Classic installed)
- A sourced ROS 2 workspace at `~/ros2_ws` containing the `sterilization_robot` package

## Quick Start — 4-Terminal Launch Sequence

The system is brought up using a fixed four-terminal sequence. Run each block in a separate terminal, in order.

### Terminal 1 — Clean & Launch Simulation

Clears any stale processes and corrupted shared-memory files from a previous run, then launches the simulation and navigation stack.

```bash
killall -9 rviz2 gazebo gzserver gzclient; pkill -f ros2; ros2 daemon stop; \
  rm -rf /dev/shm/rtps* /dev/shm/fastrtps*

cd ~/ros2_ws && source install/setup.bash
ros2 launch sterilization_robot navigation.launch.py
```

### Terminal 2 — Safe Visualization

Forces software rendering to avoid GLSL shader crashes on some Ubuntu 22.04 graphics drivers, then opens RViz2 with the Nav2 default view.

```bash
cd ~/ros2_ws && source install/setup.bash

export MESA_GL_VERSION_OVERRIDE=3.3
export MESA_GLSL_VERSION_OVERRIDE=330

rviz2 -d /opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz \
  --ros-args -p use_sim_time:=true
```

> **Note:** In the RViz Displays panel, keep **Global Costmap** and **Local Costmap** unchecked (only **Map** and **RobotModel** enabled) to avoid retriggering the shader crash described below.

### Terminal 3 — Initialize AMCL Localization

Publishes an initial pose so AMCL converges and the map/TF tree syncs correctly.

```bash
cd ~/ros2_ws && source install/setup.bash

ros2 topic pub -1 /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
  "{header: {frame_id: 'map'}, pose: {pose: {position: {x: -2.0, y: 1.0, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}}"
```

### Terminal 4 — Execute Autonomous Waypoint Tour

Runs the sterilization tour script, which sends a sequence of `NavigateToPose` goals.

```bash
cd ~/ros2_ws && source install/setup.bash

python3 src/sterilization_robot/sterilization_robot/sterilization_tour.py --ros-args -p use_sim_time:=true
```

## Troubleshooting

### Gazebo won't launch / `odom` frame missing

**Symptom:** `RTPS_TRANSPORT_SHM Error: open_and_lock_file failed`, Gazebo fails to start after an abrupt shutdown.

**Cause:** Ghost ROS 2 processes and corrupted FastRTPS shared-memory files left behind from a previous run.

**Fix:**

```bash
killall -9 rviz2 gazebo gzserver gzclient; pkill -f ros2; ros2 daemon stop; \
  rm -rf /dev/shm/rtps* /dev/shm/fastrtps*
```

Run this before every launch.

### RViz2 crashes when displaying costmaps

**Symptom:**
```
Vertex Program:rviz/glsl120/indexed_8bit_image.vert Fragment Program:rviz/glsl120/indexed_8bit_image.frag
GLSL link result: active samplers with a different type refer to the same texture image unit
```

**Cause:** Ubuntu 22.04 graphics driver incompatibility when rendering Nav2 costmaps.

**Fix:** Force software rendering and disable Costmap displays in RViz:

```bash
export MESA_GL_VERSION_OVERRIDE=3.3
export MESA_GLSL_VERSION_OVERRIDE=330
rviz2 -d /opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz --ros-args -p use_sim_time:=true
```

Then uncheck **Global Costmap** and **Local Costmap** in the Displays panel.

### TF queue full / Nav2 stuck waiting for pose

**Symptom:** `discarding message because the queue is full`; Nav2 never becomes active.

**Cause:** AMCL is waiting for an initial pose and sim-time is unsynced between the terminal and Gazebo.

**Fix:** Manually publish the initial pose:

```bash
ros2 topic pub -1 /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
  "{header: {frame_id: 'map'}, pose: {pose: {position: {x: -2.0, y: 1.0, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}}"
```

## Architecture

- **Perception:** simulated LiDAR (`base_scan`) + wheel odometry
- **Localization:** AMCL (particle filter against a static map)
- **Planning & control:** Nav2 behavior tree → `NavigateToPose` action → global/local costmaps → velocity commands
- **Simulation:** Gazebo Classic (physics + sensors)
- **Visualization:** RViz2 (map, robot model, TF) — display-only, not in the control loop

## License

Add your license here.
