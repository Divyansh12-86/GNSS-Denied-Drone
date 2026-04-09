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

```text
GNSS-Denied-Drone/
├── .gitignore
├── Dockerfile
├── README.md
├── guide.txt
├── requirements.txt
├── run_demo.sh
├── setup_env.sh
├── final_eval_flight/
│   ├── final_eval_flight_0.mcap
│   └── metadata.yaml
├── flight_data_run_1/
│   └── flight_data_run_1_0.mcap
└── src/
    ├── drone_bringup/
    │   ├── CMakeLists.txt
    │   ├── package.xml
    │   ├── config/
    │   │   └── rviz_config.rviz
    │   └── launch/
    │       └── sim_and_slam.launch.py
    ├── drone_description/
    │   ├── CMakeLists.txt
    │   ├── package.xml
    │   └── urdf/
    │       ├── drone.urdf
    │       └── quadcopter.urdf.xacro
    ├── drone_eval/
    │   ├── package.xml
    │   ├── setup.cfg
    │   ├── setup.py
    │   ├── resource/
    │   │   └── drone_eval
    │   └── drone_eval/
    │       ├── __init__.py
    │       ├── autonomous_navigator.py
    │       └── measure_latency.py
    ├── drone_gazebo/
    │   ├── CMakeLists.txt
    │   ├── package.xml
    │   └── worlds/
    │       └── dark_warehouse.sdf
    └── drone_slam/
        ├── CMakeLists.txt
        ├── package.xml
        ├── config/
        │   └── slam_params.yaml
        └── launch/
            └── slam_pipeline.launch.py
```

## ---

**🛠️ Installation and Setup**

### **1\. Prerequisites**

Ensure you are using **Ubuntu 22.04 or 24.04** with **ROS 2 (Humble or Jazzy)** and **Docker** installed.

### **2. Deployment Script**

Run the `setup_env.sh` script to automate the entire installation process. This script handles:

* Installing system-level dependencies (GStreamer for camera simulation).
* Creating a ROS-linked Python virtual environment with correct versions (e.g., `empy==3.3.4`).
* Cloning and compiling the Micro-XRCE-DDS communication bridge.
* Downloading and patching the PX4 Autopilot firmware to ignore battery and GPS failsafes for indoor flight.

```bash
chmod +x setup_env.sh run_demo.sh
./setup_env.sh
```

## ---

**🕹️ Running the Simulation**

### **1. Launch the Pipeline**

Start all logical components by running the launcher:

```bash
./run_demo.sh
```

This script opens five terminal tabs for the Bridge, Simulation, SLAM Brain, Performance Evaluator, and Autonomous Pilot.

### **2. Flight Control**

Once the Gazebo warehouse is visible:

1. Navigate to the **PX4 Terminal** tab.
2. Run the following commands in the PX4 shell:

```bash
commander set_ekf_origin 47.3977 8.5455 488.0
commander arm -f
commander takeoff
commander mode offboard
```

These commands:

* set the EKF origin for GNSS-denied operation,
* arm the motors safely for indoor flight, and
* hand off control to the autonomous navigator.

## ---

**📊 Evaluation and Reports**

### **Deliverable #3: Exporting 3D Mapping Data**

After the drone has explored the area, save the generated map from the SLAM pipeline:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/Desktop/GNSS-Denied-Drone/final_map
```

### **Deliverable #4: Performance Analysis (Drift & Latency)**

To generate the comparative report required by the Vit mentors, use the `evo` package to compare the drone's estimated trajectory against the ground truth from Gazebo:

```bash
source .venv/bin/activate
evo_ape bag final_eval_flight.mcap /fmu/out/vehicle_odometry /odom -va --plot --plot_mode xy
```

This command produces a comparative graph and calculates the Absolute Pose Error (APE) to verify that the VIO drift is below the 1.5% target.

## ---

