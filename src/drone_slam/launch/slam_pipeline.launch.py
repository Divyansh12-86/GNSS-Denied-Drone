import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    param_file = os.path.expanduser('~/drone_sitl_ws/src/drone_slam/config/slam_params.yaml')
    return LaunchDescription([
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[param_file, {'use_sim_time': True}]
        )
    ])