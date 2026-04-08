FROM osrf/ros:jazzy-desktop
RUN apt-get update && apt-get install -y ros-jazzy-slam-toolbox ros-jazzy-ros-gz && rm -rf /var/lib/apt/lists/*
WORKDIR /edge_ws
COPY ./src /edge_ws/src
RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && colcon build"
RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
RUN echo "source /edge_ws/install/setup.bash" >> ~/.bashrc
CMD ["/bin/bash", "-c", "source /edge_ws/install/setup.bash && ros2 launch drone_slam slam_pipeline.launch.py"]