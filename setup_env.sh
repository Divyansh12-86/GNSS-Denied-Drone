#!/bin/bash
# ==========================================
# GNSS-Denied Drone: Automatic Environment Setup
# ==========================================

WORKSPACE_DIR=$(pwd)

echo "📦 Installing System Dependencies (GStreamer, Python, etc.)..."
sudo apt-get update
sudo apt-get install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev python3-venv python3-pip

# 1. Setup Virtual Environment
echo "🐍 Creating Python Virtual Environment..."
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -r requirements.txt
# Critical PX4 build fixes
pip install kconfiglib jinja2 jsonschema empy==3.3.4 pexpect pyros-genmsg

# 2. Setup ROS 2 Bridge
if [ ! -d "$HOME/Micro-XRCE-DDS-Agent" ]; then
    echo "🌉 Installing Micro-XRCE-DDS-Agent..."
    cd ~ && git clone https://github.com/eProsima/Micro-XRCE-DDS-Agent.git
    cd Micro-XRCE-DDS-Agent && mkdir build && cd build
    cmake .. && make && sudo make install && sudo ldconfig /usr/local/lib/
fi

# 3. Setup PX4 Autopilot
if [ ! -d "$HOME/PX4-Autopilot" ]; then
    echo "🚁 Cloning PX4 Autopilot..."
    cd ~ && git clone https://github.com/PX4/PX4-Autopilot.git --recursive
    bash ./PX4-Autopilot/Tools/setup/ubuntu.sh
fi

# 4. CRITICAL: Automatic Airframe Patching (The "Fuss" Fix)
# This appends the safety overrides to the default x500 config automatically
echo "🛠️ Patching PX4 Airframe for GNSS-Denied flight..."
AF_FILE="$HOME/PX4-Autopilot/ROMFS/px4fmu_common/init.d-posix/airframes/4001_gz_x500"
if ! grep -q "GNSS-DENIED" "$AF_FILE"; then
    cat <<EOT >> "$AF_FILE"

# GNSS-DENIED SIMULATION OVERRIDES
param set-default CBRK_SUPPLY_CHK 894281
param set-default COM_LOW_BAT_ACT 0
param set-default COM_ARM_WO_GPS 1
param set-default COM_ARM_MAG_STR 0
param set-default EKF2_MAG_TYPE 5
param set-default NAV_DLL_ACT 0
param set-default NAV_RCL_ACT 0
EOT
fi

# 5. Build Workspace
echo "🔨 Building ROS 2 Workspace..."
cd $WORKSPACE_DIR
colcon build --symlink-install

echo "✅ Setup Complete! To fly, run: ./run_demo.sh"