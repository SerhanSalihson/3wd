# 3WD Omni Robot

ROS 2 Jazzy simulation for a three-wheel omnidirectional robot with Gazebo,
SLAM Toolbox, and Nav2.

## Run

```bash
cd ~/omni
source /opt/ros/jazzy/setup.bash
colcon build --packages-select omni_wheel_controller omni --symlink-install
source install/setup.bash
ros2 launch omni quickstart.launch.py
```

In RViz, select **Nav2 Goal**, then click and drag on the map to set the
destination and heading. Nav2 plans and drives the robot while SLAM continues
updating the map.

## Quick Launcher

```bash
cd ~/omni
./quick_launch.sh
```

Choose **Navigation** for Gazebo, SLAM, Nav2, and RViz. Choose **SLAM Mapping**
for Gazebo, SLAM, and RViz without starting Nav2.

The same modes are available directly:

```bash
ros2 launch omni quickstart.launch.py navigation:=true
ros2 launch omni quickstart.launch.py navigation:=false
```
