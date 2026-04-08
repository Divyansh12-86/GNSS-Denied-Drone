#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

class MeasureLatency(Node):
    def __init__(self):
        super().__init__('measure_latency')
        # Add logic to measure latency

def main(args=None):
    rclpy.init(args=args)
    node = MeasureLatency()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()