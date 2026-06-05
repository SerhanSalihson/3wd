#!/bin/bash
# Quick launch script for omni robot

echo "╔════════════════════════════════════════════╗"
echo "║     OMNI ROBOT QUICK LAUNCHER              ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Choose an option:"
echo ""
echo "  1) Navigation: Gazebo + SLAM + Nav2 + RViz"
echo "  2) SLAM Mapping: Gazebo + SLAM + RViz"
echo "  3) Launch Gazebo Simulation only"
echo "  4) Launch Keyboard Teleop only"
echo "  5) Launch Robot State Publisher only"
echo "  6) Build workspace"
echo "  7) Exit"
echo ""
read -p "Enter choice [1-7]: " choice

cd ~/omni
source install/setup.bash

case $choice in
    1)
        echo "Launching Gazebo + SLAM + Nav2 + RViz..."
        ros2 launch omni quickstart.launch.py navigation:=true
        ;;
    2)
        echo "Launching Gazebo + SLAM + RViz mapping mode..."
        ros2 launch omni quickstart.launch.py navigation:=false
        ;;
    3)
        echo "Launching Gazebo..."
        ros2 launch omni gazebo.launch.py
        ;;
    4)
        echo "Launching Keyboard Teleop..."
        echo "Use WASD to control, SPACE to stop, ESC to quit"
        ros2 run omni keyboard_teleop.py
        ;;
    5)
        echo "Launching Robot State Publisher..."
        echo "Open RViz2 in another terminal to visualize"
        ros2 launch omni rsp.launch.py
        ;;
    6)
        echo "Building workspace..."
        colcon build --symlink-install
        ;;
    7)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac
