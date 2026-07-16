from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="mavros",
            executable="mavros_node",
            name="mavros",
            output="screen",
            parameters=[{
                "fcu_url": "udp://127.0.0.1:14540@14557",
                "gcs_url": "",
                "tgt_system": 1,
                "tgt_component": 1,
                "fcu_protocol": "v2.0",
                "plugin_blacklist": ["companion_process_status"],
            }],
        ),
        Node(
            package="uav_control",
            executable="keyboard_teleop",
            name="keyboard_teleop",
            output="screen",
            prefix="xterm -e",  # gives it its own terminal for raw keyboard input
        ),
    ])