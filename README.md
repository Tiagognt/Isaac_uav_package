## Pour le lancement des nodes du package de controle par le clavier:

- Pour le node mavros:

```
	source /opt/ros/humble/setup.bash
source ~/HermesPerso/ros_ws/install/setup.bash

ros2 run mavros mavros_node --ros-args \
  -p fcu_url:=udp://127.0.0.1:14540@14557 \
  -p tgt_system:=1 \
  -p tgt_component:=1 \
  -p fcu_protocol:=v2.0 \
  --params-file ~/HermesPerso/ros_ws/install/uav_control/share/uav_control/config/mavros_plugins.yaml
  
 ```
 
 - Pour le node du clavier:
 
 ```
 	source /opt/ros/humble/setup.bash
source ~/HermesPerso/ros_ws/install/setup.bash

ros2 run uav_control keyboard_teleop
 
 ```