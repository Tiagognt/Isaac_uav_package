# Isaac UAV Package — Simulation Launch Guide

This guide explains how to launch the UAV simulation together with keyboard controls.

## Prerequisites

Before you start, make sure you have:

- **Isaac Sim 5.1** installed.
- **Pegasus Simulator** installed for the **same version** (5.1). If it isn't installed yet, follow the official installation guide: https://pegasussimulator.github.io/PegasusSimulator/source/setup/installation.html
- A working **ROS 2** installation, **sourced in every terminal** you open.

> **Tip:** Replace `YOUR_USERNAME` and `PATH_TO_WHERE_YOU_CLONED` in the commands below with your own values. To make things easier, you can define the repo path once per terminal:
> ```bash
> export UAV_PKG=/home/YOUR_USERNAME/PATH_TO_WHERE_YOU_CLONED/Isaac-uav-package
> ```
> Then use `$UAV_PKG` wherever the path appears.

## How to launch

The simulation runs across **3 separate terminals**. Launch them **in order** and **wait for each process to finish starting** before moving to the next — Isaac Sim Classic can lag noticeably on startup.

### Terminal 1 — Simulation environment

```bash
cd /home/YOUR_USERNAME/PATH_TO_WHERE_YOU_CLONED/Isaac-uav-package/ros_ws/src/uav_control/scripts/
isaac_run spawn_uav.py
```

### Terminal 2 — MAVROS node (communication with the UAV)

```bash
source /opt/ros/humble/setup.bash
source /home/YOUR_USERNAME/PATH_TO_WHERE_YOU_CLONED/Isaac-uav-package/ros_ws/install/setup.bash

ros2 run mavros mavros_node --ros-args \
  -p fcu_url:=udp://127.0.0.1:14540@14557 \
  -p tgt_system:=1 \
  -p tgt_component:=1 \
  -p fcu_protocol:=v2.0 \
  --params-file /home/YOUR_USERNAME/PATH_TO_WHERE_YOU_CLONED/Isaac-uav-package/ros_ws/install/uav_control/share/uav_control/config/mavros_plugins.yaml
```

### Terminal 3 — Keyboard teleop (controls)

```bash
source /opt/ros/humble/setup.bash
source /home/YOUR_USERNAME/PATH_TO_WHERE_YOU_CLONED/Isaac-uav-package/ros_ws/install/setup.bash

ros2 run uav_control keyboard_teleop
```

Once all three are running, keep the **Terminal 3** window focused to send keyboard commands to the UAV.