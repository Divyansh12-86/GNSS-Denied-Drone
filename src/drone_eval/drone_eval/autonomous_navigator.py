import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import math

class AutonomousNavigator(Node):
    def __init__(self):
        super().__init__('autonomous_navigator')
        
        # 1. Create Publisher to send flight commands to the drone
        # Note: Change 'cmd_vel' if your drone uses a specific namespace like '/drone/cmd_vel'
        self.cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        
        # 2. Create Subscriber to listen to the LIDAR scanner
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10 # QoS profile depth
        )

        # 3. Flight Parameters
        self.safe_distance = 1.5  # meters (starts turning if a wall is closer than this)
        self.forward_speed = 0.5  # m/s
        self.turn_speed = 0.5     # rad/s

        self.get_logger().info("Autonomous Navigator Started! Searching for open space...")

    def scan_callback(self, msg):
        """
        This function runs every single time a new LIDAR scan is received.
        It evaluates the surroundings and immediately publishes a movement command.
        """
        # Create an empty Twist message (defaults to 0 speed)
        command = Twist()

        # The ranges array contains distances to obstacles. 
        # We divide the front 180 degrees into Left, Front, and Right regions.
        total_rays = len(msg.ranges)
        
        # Calculate indices for the regions (Assuming 0 is straight ahead, depending on LIDAR setup)
        # If your LIDAR 0-index is the back of the drone, you'll need to shift these.
        # Standard ROS REP-117 dictates 0 is straight ahead, spinning counter-clockwise.
        
        front_rays = msg.ranges[0:20] + msg.ranges[-20:] # ±20 degrees from center
        left_rays = msg.ranges[20:90]                    # 20 to 90 degrees (Left)
        right_rays = msg.ranges[-90:-20]                 # -90 to -20 degrees (Right)

        # Filter out 'inf' (infinity) and 0.0 values which represent no return/errors
        valid_front = [r for r in front_rays if not math.isinf(r) and r > 0.1]
        valid_left = [r for r in left_rays if not math.isinf(r) and r > 0.1]
        valid_right = [r for r in right_rays if not math.isinf(r) and r > 0.1]

        # Find the minimum distance (closest obstacle) in each region
        # If no valid readings, assume it is completely clear (10.0 meters)
        min_front = min(valid_front) if valid_front else 10.0
        min_left = min(valid_left) if valid_left else 10.0
        min_right = min(valid_right) if valid_right else 10.0

        # --- THE DECISION LOGIC ---
        
        if min_front > self.safe_distance:
            # Path is clear! Fly straight.
            command.linear.x = self.forward_speed
            command.angular.z = 0.0
            self.get_logger().debug("Path clear. Moving forward.")
            
        else:
            # Obstacle detected ahead! Stop moving forward and decide which way to turn.
            command.linear.x = 0.0 
            
            if min_left > min_right:
                # Left side has more room, turn Left (positive angular velocity)
                command.angular.z = self.turn_speed
                self.get_logger().info(f"Wall ahead! Turning LEFT (Left: {min_left:.1f}m, Right: {min_right:.1f}m)")
            else:
                # Right side has more room, turn Right (negative angular velocity)
                command.angular.z = -self.turn_speed
                self.get_logger().info(f"Wall ahead! Turning RIGHT (Left: {min_left:.1f}m, Right: {min_right:.1f}m)")

        # 4. Send the command to the drone
        self.cmd_pub.publish(command)

def main(args=None):
    rclpy.init(args=args)
    navigator = AutonomousNavigator()
    
    try:
        # Spin keeps the node alive and listening for LIDAR callbacks
        rclpy.spin(navigator)
    except KeyboardInterrupt:
        pass
    finally:
        # Clean shutdown
        navigator.cmd_pub.publish(Twist()) # Send a 0 speed command to stop the drone
        navigator.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()