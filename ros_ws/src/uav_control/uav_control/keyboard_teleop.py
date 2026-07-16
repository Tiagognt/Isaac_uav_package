#!/usr/bin/env python3
import sys
import select
import termios
import tty
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, SetMode, CommandTOL

INSTRUCTIONS = """
UAV Keyboard Teleop
--------------------------------
w/s : forward / backward
a/d : left / right
r/f : up / down
q/e : yaw left / yaw right
SPACE : zero velocity (hover)
o : arm + switch to OFFBOARD
l : disarm
t : takeoff
g : land
CTRL+C : quit
--------------------------------
"""

LIN_STEP = 1.0
YAW_STEP = 1.0
SERVICE_WAIT_TIMEOUT = 5.0  # give MAVROS time to fully come up


class KeyboardTeleop(Node):
    def __init__(self):
        super().__init__('keyboard_teleop')

        self.pub = self.create_publisher(
            TwistStamped, '/mavros/setpoint_velocity/cmd_vel', 10)

        self.arm_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.mode_client = self.create_client(SetMode, '/mavros/set_mode')
        self.takeoff_client = self.create_client(CommandTOL, '/mavros/cmd/takeoff')
        self.land_client = self.create_client(CommandTOL, '/mavros/cmd/land')

        self.state_sub = self.create_subscription(
            State, '/mavros/state', self.state_cb, 10)
        self.connected = False
        self.armed = False
        self.mode = ''

        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0
        self.yaw_rate = 0.0

        self.timer = self.create_timer(1.0 / 20.0, self.publish_setpoint)

        self.settings = termios.tcgetattr(sys.stdin)
        self.get_logger().info(INSTRUCTIONS)

    def state_cb(self, msg: State):
        self.connected = msg.connected
        self.armed = msg.armed
        self.mode = msg.mode

    def publish_setpoint(self):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        msg.twist.linear.x = self.vx
        msg.twist.linear.y = self.vy
        msg.twist.linear.z = self.vz
        msg.twist.angular.z = self.yaw_rate
        self.pub.publish(msg)

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        key = sys.stdin.read(1) if rlist else ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def call_arm(self, value: bool) -> bool:
        if not self.connected:
            self.get_logger().warn('Not connected to FCU yet — ignoring arm request')
            return False
        if not self.arm_client.wait_for_service(timeout_sec=SERVICE_WAIT_TIMEOUT):
            self.get_logger().error('Arming service not available after waiting')
            return False
        req = CommandBool.Request()
        req.value = value
        future = self.arm_client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=SERVICE_WAIT_TIMEOUT)
        if future.result() is not None and future.result().success:
            self.get_logger().info(f'Arm={value} succeeded')
            return True
        self.get_logger().error(f'Arm={value} FAILED: {future.result()}')
        return False

    def call_offboard(self) -> bool:
        if not self.mode_client.wait_for_service(timeout_sec=SERVICE_WAIT_TIMEOUT):
            self.get_logger().error('SetMode service not available after waiting')
            return False
        req = SetMode.Request()
        req.custom_mode = 'OFFBOARD'
        future = self.mode_client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=SERVICE_WAIT_TIMEOUT)
        if future.result() is not None and future.result().mode_sent:
            self.get_logger().info('OFFBOARD mode request sent successfully')
            return True
        self.get_logger().error(f'OFFBOARD request FAILED: {future.result()}')
        return False

    def call_takeoff(self):
        if not self.takeoff_client.wait_for_service(timeout_sec=SERVICE_WAIT_TIMEOUT):
            self.get_logger().error('Takeoff service not available')
            return
        req = CommandTOL.Request()
        req.latitude = math.nan   # NaN = use current position
        req.longitude = math.nan  # NaN = use current position
        req.altitude = 2.0        # relative takeoff altitude, meters
        future = self.takeoff_client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=SERVICE_WAIT_TIMEOUT)
        if future.result() is not None and future.result().success:
            self.get_logger().info('Takeoff command accepted')
        else:
            self.get_logger().error(f'Takeoff FAILED: {future.result()}')

    def call_land(self):
        if not self.land_client.wait_for_service(timeout_sec=SERVICE_WAIT_TIMEOUT):
            self.get_logger().error('Land service not available')
            return
        req = CommandTOL.Request()
        future = self.land_client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=SERVICE_WAIT_TIMEOUT)
        if future.result() is not None and future.result().success:
            self.get_logger().info('Land command accepted')
        else:
            self.get_logger().error(f'Land FAILED: {future.result()}')

    def run(self):
        try:
            while rclpy.ok():
                key = self.get_key()

                if key == 'w':
                    self.vx = LIN_STEP
                elif key == 's':
                    self.vx = -LIN_STEP
                elif key == 'a':
                    self.vy = -LIN_STEP
                elif key == 'd':
                    self.vy = LIN_STEP
                elif key == 'r':
                    self.vz = LIN_STEP
                elif key == 'f':
                    self.vz = -LIN_STEP
                elif key == 'q':
                    self.yaw_rate = YAW_STEP
                elif key == 'e':
                    self.yaw_rate = -YAW_STEP
                elif key == ' ':
                    self.vx = self.vy = self.vz = self.yaw_rate = 0.0
                elif key == 'o':
                    if self.call_arm(True):
                        self.call_offboard()
                elif key == 'l':
                    self.vx = self.vy = self.vz = self.yaw_rate = 0.0
                    self.call_arm(False)
                elif key == 't':
                    self.call_takeoff()
                elif key == 'g':
                    self.call_land()
                elif key == '\x03':
                    break

                rclpy.spin_once(self, timeout_sec=0.0)
        except KeyboardInterrupt:
            pass
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)


def main(args=None):
    rclpy.init(args=args)
    node = KeyboardTeleop()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()