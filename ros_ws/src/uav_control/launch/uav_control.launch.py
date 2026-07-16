from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    plugin_config = os.path.join(
        get_package_share_directory('uav_control'),
        'config',
        'mavros_plugins.yaml'
    )

    return LaunchDescription([
        Node(
            package="mavros",
            executable="mavros_node",
            name="mavros",
            output="screen",
            parameters=[
                {
                    "fcu_url": "udp://127.0.0.1:14540@14580",
                    "gcs_url": "",
                    "tgt_system": 1,
                    "tgt_component": 1,
                    "fcu_protocol": "v2.0",
                },
                plugin_config,
            ],
        ),
        Node(
        package="uav_control",
            executable="keyboard_teleop",
            name="keyboard_teleop",
            output="screen",
            prefix="xterm -e",
        ),
    ])  