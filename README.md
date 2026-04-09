# **DP4: Autonomous Navigator for GNSS-Denied Environments (SITL Prototype)**

## **📌 Project Overview**

This project is a comprehensive Software-In-The-Loop (SITL) demonstration of an autonomous Unmanned Aerial Vehicle (UAV) specifically designed for exploration and high-resolution 3D mapping in GNSS-denied environments. These environments, such as underground tunnels and dark warehouses, lack GPS signals and sufficient lighting, presenting significant challenges for standard navigation systems.  
To simulate a real-world deployment on an edge device like an NVIDIA Jetson, the architecture isolates computationally intensive SLAM (Simultaneous Localization and Mapping) algorithms within a constrained Docker container. This proves that the system can maintain a SLAM pipeline latency of less than 50ms while operating in extreme conditions.

## ---

**🎯 Goals and Design Considerations**

The project is built to meet strict performance metrics as defined in the DP4 evaluation criteria:

* **State Estimation:** Maintain Visual-Inertial Odometry (VIO) drift of less than 1.5% over a 200-meter flight path.  
* **Environmental Resilience:** Successful operation in low-light environments with less than 15 lux of ambient light.  
* **Onboard Processing:** A complete SLAM pipeline that maintains processing latency under 50ms.  
* **Form Factor:** A drone footprint contained within a 350mm x 350mm boundary.

## ---

**📦 Deliverables Addressed**

This repository fulfills all five core deliverables for the DP4 evaluation:

1. **Hardware/Software Prototype:** A fully functional ROS 2 and Gazebo SITL architecture.  
2. **Digital Twin & Simulation:** A custom-built Gazebo world replicating a dark warehouse with a high-fidelity simulated quadcopter.  
3. **3D Mapping Data:** Generation of high-resolution point clouds and 2D occupancy maps of the explored area.  
4. **Performance Report:** Comparative trajectory analysis (Estimated vs. Ground Truth) and automated latency benchmarking.  
5. **Source Code:** A documented ROS 2 workspace including custom navigation, evaluation, and deployment scripts.

## ---

**🧠 System Architecture**

The system utilizes a split-architecture to emulate edge computing:

* **Host Environment (SITL):** Runs the Gazebo physics engine and the PX4 Autopilot firmware. Gazebo simulates the dark warehouse and generates raw sensor data from a simulated 3D LiDAR and Stereo Camera.  
* **Edge Brain (Docker):** A containerized ROS 2 environment that handles the "heavy lifting" of SLAM. It processes sensor data and returns odometry to the flight controller, simulating an onboard computer with restricted resources.

## ---

**📂 Project Structure**

Plaintext

GNSS-Denied-Drone/  
├── .venv/                      \# Python virtual environment (auto-generated)  
├── setup\_env.sh                \# Automated dependency and PX4 patching script  
├── run\_demo.sh                 \# One-click multi-terminal simulation launcher  
├── requirements.txt            \# Python libraries for evaluation (evo, matplotlib)  
├── README.md                   \# Project documentation  
└── src/  
    ├── drone\_gazebo/           \# Digital Twin: Custom warehouse world and models  
    ├── drone\_eval/             \# Performance: Latency measurement and navigator nodes  
    └── drone\_bringup/          \# Deployment: Master launch and Rviz configurations

## ---

**🛠️ Installation and Setup**

### **1\. Prerequisites**

Ensure you are using **Ubuntu 22.04 or 24.04** with **ROS 2 (Humble or Jazzy)** and **Docker** installed.

### **2\. Deployment Script**

Run the setup\_env.sh script to automate the entire installation process. This script handles:

* Installing system-level dependencies (GStreamer for camera simulation).  
* Creating a ROS-linked Python virtual environment with correct versions (e.g., empy==3.3.4).  
* Cloning and compiling the Micro-XRCE-DDS communication bridge.  
* Downloading and patching the PX4 Autopilot firmware to ignore battery and GPS failsafes for indoor flight.

Bash

chmod \+x setup\_env.sh run\_demo.sh  
./setup\_env.sh

## ---

**🕹️ Running the Simulation**

### **1\. Launch the Pipeline**

Start all logical components by running the launcher:

Bash

./run\_demo.sh

This script opens five terminal tabs for the Bridge, Simulation, SLAM Brain, Performance Evaluator, and Autonomous Pilot.

### **2\. Flight Control**

Once the Gazebo warehouse is visible:

1. Navigate to the **PX4 Terminal** tab.  
2. **Set Origin:** commander set\_ekf\_origin 47.3977 8.5455 488.0 (Gives the drone a "Home" in the absence of GPS).  
3. **Arm:** commander arm \-f (Forces the motors to spin despite sensor warnings).  
4. **Takeoff:** commander takeoff (Climbs to 2.5 meters).  
5. **Autonomous Mode:** commander mode offboard (Hands steering control to the Python Navigator).

## ---

**📊 Evaluation and Reports**

### **Deliverable \#3: Exporting 3D Mapping Data**

After the drone has explored the area, save the generated map from the SLAM pipeline:

Bash

ros2 run nav2\_map\_server map\_saver\_cli \-f \~/Desktop/GNSS-Denied-Drone/final\_map

### **Deliverable \#4: Performance Analysis (Drift & Latency)**

To generate the comparative report required by the Vit mentors, use the evo package to compare the drone's estimated trajectory against the ground truth from Gazebo:

Bash

source .venv/bin/activate  
evo\_ape bag final\_eval\_flight.mcap /fmu/out/vehicle\_odometry /odom \-va \--plot \--plot\_mode xy

This command produces a comparative graph and calculates the Absolute Pose Error (APE) to verify that the VIO drift is below the 1.5% target.

## ---

