# GNSS-Denied Autonomous UAV Navigation (SITL Prototype)

## 📌 Project Overview
This project is a Software-In-The-Loop (SITL) demonstration of an autonomous UAV designed for exploration and 3D mapping in GNSS-denied environments (e.g., underground tunnels, dark warehouses). 

Because physical hardware (like an Nvidia Jetson and a physical drone frame) is substituted with a simulation, this architecture deliberately isolates the computationally heavy SLAM algorithms into a constrained environment (Docker) to prove edge-compute feasibility.

### 🎯 Deliverables Addressed
1. **Hardware/Software Prototype:** Replaced with a ROS 2 / Gazebo SITL architecture.
2. **Digital Twin:** A custom Gazebo world replicating a low-light (< 15 lux) warehouse.
3. **3D Mapping:** Point cloud generation using [Insert your chosen SLAM, e.g., RTAB-Map].
4. **Performance Report:** Built-in Python evaluation nodes to prove VIO drift < 1.5% and SLAM latency < 50ms.
5. **Source Code:** This documented ROS 2 `colcon` workspace.

---

## 🧠 System Architecture & Logic

To convincingly simulate a physical drone, the system is divided into two logical halves:

1. **The Environment & Flight Controller (Host PC):** Gazebo simulates the physics, the dark warehouse environment, and the raw sensor data (Stereo Camera/LiDAR). A simulated flight controller (like PX4 SITL) keeps the drone stable.
2. **The "Edge Compute" Brain (Docker Container):** To prove that our SLAM algorithm can run on an edge device (like a Jetson Nano) with strict < 50ms latency, the SLAM nodes run inside an isolated Docker container with artificially restricted CPU and RAM. This container subscribes to Gazebo's sensor topics, processes the 3D map, and publishes the estimated Odometry back to the flight controller.

---

## 📂 Complete Project Structure

Below is the exhaustive file and directory structure for this ROS 2 workspace:

<pre>
drone_sitl_ws/
├── Dockerfile                      # Your edge compute emulator configuration
├── requirements.txt                # Python dependencies for evaluation scripts
├── README.md                       # This project documentation
└── src/
    ├── drone_bringup/              # Master launch package
    │   ├── CMakeLists.txt
    │   ├── package.xml
    │   ├── launch/
    │   │   └── sim_and_slam.launch.py
    │   └── config/
    │       └── rviz_config.rviz    # Saves visualization window layout
    ├── drone_description/          # The 3D model (<350mm constraint)
    │   ├── CMakeLists.txt
    │   ├── package.xml
    │   ├── urdf/
    │   │   └── quadcopter.urdf.xacro # The exact physical/sensor definitions
    │   └── meshes/
    │       └── drone_frame.dae     # Visual CAD files for the drone body
    ├── drone_gazebo/               # The environment (<15 lux constraint)
    │   ├── CMakeLists.txt
    │   ├── package.xml
    │   ├── worlds/
    │   │   └── dark_warehouse.world 
    │   └── models/
    │       └── warehouse_walls/    # 3D assets for the simulation world
    │           ├── model.sdf
    │           └── model.config
    ├── drone_slam/                 # The "Jetson Brain" SLAM implementation
    │   ├── CMakeLists.txt
    │   ├── package.xml
    │   ├── launch/
    │   │   └── slam_pipeline.launch.py # Launched inside Docker container
    │   └── config/
    │       └── slam_params.yaml    # SLAM algorithm tuning
    └── drone_eval/                 # Evaluation scripts (Python package)
        ├── setup.py                # Build instructions for Python ROS 2 nodes
        ├── setup.cfg
        ├── package.xml
        ├── resource/
        │   └── drone_eval          # Required blank marker file
        └── drone_eval/
            ├── __init__.py
            └── measure_latency.py  # Script calculating <50ms constraint
</pre>

---

## ⚙️ Prerequisites

Before running this project, ensure you have the following installed on an Ubuntu 22.04 system:
* [ROS 2 Humble](https://docs.ros.org/en/humble/Installation.html)
* [Gazebo Classic 11](https://classic.gazebosim.org/tutorials?tut=ros2_installing)
* [Docker](https://docs.docker.com/engine/install/ubuntu/)
* Python 3.10+

---

## 🚀 Installation & Setup

**1. Clone the repository and install dependencies:**

```bash
mkdir -p ~/drone_sitl_ws/src
cd ~/drone_sitl_ws
# (Clone or copy your project files into the src directory here)

# Install Python requirements for the evaluation scripts
pip install -r requirements.txt

# Install ROS 2 dependencies using rosdep
rosdep update
rosdep install --from-paths src --ignore-src -r -y

**2. Build the Host Workspace (Simulation):**
\`\`\`bash
cd ~/drone_sitl_ws
colcon build --symlink-install
source install/setup.bash
\`\`\`

**3. Build the Edge Docker Image:**
\`\`\`bash
cd ~/drone_sitl_ws
docker build -t drone_edge_brain .
\`\`\`

---

## 🕹️ Usage Instructions (The Demonstration)

To run the full SITL demonstration, follow these steps in separate terminal windows.

**Step 1: Launch the Simulated World**
This starts Gazebo with the dark warehouse and spawns the drone.
\`\`\`bash
source ~/drone_sitl_ws/install/setup.bash
ros2 launch drone_bringup sim_and_slam.launch.py
\`\`\`

**Step 2: Start the "Edge" SLAM Brain**
This launches the Docker container, simulating the Jetson's onboard processing. It limits the container to 4 CPU cores and 4GB of RAM.
\`\`\`bash
docker run --net=host --cpus="4" --memory="4g" drone_edge_brain
\`\`\`

**Step 3: Run the Performance Evaluators**
While the drone is exploring, run the custom scripts to measure latency and record the trajectory for the drift report.
\`\`\`bash
source ~/drone_sitl_ws/install/setup.bash
ros2 run drone_eval measure_latency.py
\`\`\`

**Step 4: Generate the Drift Report**
After stopping the simulation, use `evo` to compare the SLAM trajectory against Gazebo's ground truth.
\`\`\`bash
evo_traj odom /slam/odom --ref /gazebo/ground_truth -p --plot_mode xy
\`\`\`