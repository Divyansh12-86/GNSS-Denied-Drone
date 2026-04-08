import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    world_path = os.path.expanduser('~/Desktop/GNSS-Denied-Drone/src/drone_gazebo/worlds/dark_warehouse.sdf')
    urdf_path = os.path.expanduser('~/Desktop/GNSS-Denied-Drone/src/drone_description/urdf/drone.urdf')

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': f'-r {world_path}'}.items(),
    )
    spawn_drone = ExecuteProcess(
        cmd=['ros2', 'run', 'ros_gz_sim', 'create', '-file', urdf_path, '-name', 'my_drone', '-z', '0.5'],
        output='screen'
    )
    bridge = ExecuteProcess(
        cmd=['ros2', 'run', 'ros_gz_bridge', 'parameter_bridge', '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'],
        output='screen'
    )
    return LaunchDescription([gz_sim, spawn_drone, bridge])