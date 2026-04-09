#!/bin/bash
# ====================================================
# GNSS-Denied Drone: One-Click Simulation Launcher
# ====================================================

WORKSPACE_DIR=$(pwd)

echo "🚀 Launching GNSS-Denied SITL Pipeline..."

# 1. Start Micro-XRCE-DDS Agent (Communication Bridge)
gnome-terminal --tab --title="1. DDS Bridge" -- bash -c "MicroXRCEAgent udp4 -p 8888; exec bash"

# 2. Start PX4 Simulation (Digital Twin)
# We copy the world file to ensure it loads and export the name only to avoid path bugs.
gnome-terminal --tab --title="2. PX4 & Gazebo" -- bash -c "
cp $WORKSPACE_DIR/src/drone_gazebo/worlds/dark_warehouse.sdf ~/PX4-Autopilot/Tools/simulation/gz/worlds/;
export PX4_GZ_WORLD=dark_warehouse;
cd ~/PX4-Autopilot;
make px4_sitl gz_x500; exec bash"

echo "Waiting for Gazebo to load textures (15 seconds)..."
sleep 15

# 3. Start SLAM Brain (3D Mapping - Deliverable 3)
gnome-terminal --tab --title="3. SLAM Brain" -- bash -c "docker run --net=host --cpus='4' --memory='4g' -v $WORKSPACE_DIR:/root/drone_sitl_ws drone_edge_brain; exec bash"

# 4. Start Performance Evaluators (Deliverable 4)
gnome-terminal --tab --title="4. Evaluator" -- bash -c "
cd $WORKSPACE_DIR;
source .venv/bin/activate;
source install/setup.bash;
echo 'Recording Performance Data...';
ros2 bag record -o final_eval_flight /fmu/out/vehicle_odometry /odom /tf &
ros2 run drone_eval measure_latency; exec bash"

# 5. Start the Autonomous Pilot (Deliverable 5)
# Tab 5: Pilot & Origin Setup
gnome-terminal --tab --title="5. Pilot" -- bash -c "
cd $WORKSPACE_DIR;
source .venv/bin/activate;
source install/setup.bash;
echo 'Warm up...';
sleep 15;
# Force the origin so 'takeoff' becomes available
commander set_ekf_origin 47.3977 8.5455 488.0; 
ros2 run drone_eval autonomous_navigator; exec bash"