# RC MMR Simulation & Controls (`rc_mmr_sim`)

This repository contains the simulation overlay packages for the **A300 Mobile Manipulator Robot (MMR)**. It provides complete integration with **Gazebo Sim**, **Nav2 Navigation**, **SLAM**, and **MoveIt 2** for manipulator control, built on top of standard ROS 2 (Jazzy Jalisco).

> [!NOTE]
> This repository is a sub-module/component of the main development workspace repository:
> [rc-robocup Dev Environment](https://github.com/Adyansh04/rc-robocup)

---

## 📦 Package Directory

Here is the list of ROS 2 packages included in this repository:

| Package | Description |
|---|---|
| [**`rc_common`**](./rc_common) | Dynamic package-share config tracker. Holds robot parameters (`robot.yaml`), configurations (`robot.urdf.xacro`, `robot.srdf`), and launch files for sensor/platform services. |
| [**`rc_control`**](./rc_control) | Platform teleoperation controls, joystick support, and base localization. |
| [**`rc_gz`**](./rc_gz) | Gazebo simulation setup, containing world definitions, spawn scripts, and bridges. |
| [**`rc_manipulators`**](./rc_manipulators) | MoveIt 2 configuration, launch scripts, and controller managers for the arm manipulator. |
| [**`rc_manipulators_description`**](./rc_manipulators_description) | URDF / Xacro description files specific to the arm manipulator. |
| [**`rc_nav2_demos`**](./rc_nav2_demos) | Nav2 stack configuration, path planning, slam maps, and navigation scripts. |
| [**`rc_platform_description`**](./rc_platform_description) | URDF / Xacro description files specific to the A300 mobile base platform. |
| [**`rc_sensors_description`**](./rc_sensors_description) | URDF / Xacro description files for LiDAR, camera, and IMU sensors. |
| [**`rc_viz`**](./rc_viz) | Rviz2 pre-configured layouts and visualization launching scripts. |

---

## 🚀 Running the Demos

> [!IMPORTANT]
> Make sure you are running these commands inside your active ROS 2 container (`ros-dev`).
> Before running any commands, build the workspace and source the setup files:
> ```bash
> cd /root/workspace
> colcon build --symlink-install
> source install/setup.bash
> ```

### 🗺️ 1. Mapping & SLAM (gmapping)
Use these commands to launch the simulator, Nav2, SLAM, visualization, and save your generated map.

1. **Start the Gazebo Simulation:**
   ```bash
   ros2 launch rc_gz simulation.launch.py
   ```
2. **Launch Nav2 Stack:** (in a new terminal)
   ```bash
   ros2 launch rc_nav2_demos nav2.launch.py use_sim_time:=true
   ```
3. **Start SLAM for Mapping:** (in a new terminal)
   ```bash
   ros2 launch rc_nav2_demos slam.launch.py use_sim_time:=true
   ```
4. **View Navigation in RViz:** (in a new terminal)
   ```bash
   ros2 launch rc_viz view_navigation.launch.py namespace:=/rc use_sim_time:=true
   ```
5. **Save the Map:**
   When you are satisfied with the mapped area, run the following command to save it (the saved map files `my_map.yaml` and `my_map.pgm` will be generated in your current working directory):
   ```bash
   ros2 run nav2_map_server map_saver_cli -f "my_map" --ros-args -p map_subscribe_transient_local:=true -r __ns:=/rc
   ```

---

### 🧭 2. Autonomous Navigation (Nav2)
Once you have saved a map, you can run navigation with localization.

1. **Start the Gazebo Simulation:**
   ```bash
   ros2 launch rc_gz simulation.launch.py
   ```
2. **Launch Nav2 Stack:** (in a new terminal)
   ```bash
   ros2 launch rc_nav2_demos nav2.launch.py use_sim_time:=true
   ```
3. **Launch Localization:** (in a new terminal, make sure to execute from the directory where `my_map.yaml` was saved, or provide its full path):
   ```bash
   ros2 launch rc_nav2_demos localization.launch.py map:=my_map.yaml use_sim_time:=true
   ```
4. **View in RViz:** (in a new terminal)
   ```bash
   ros2 launch rc_viz view_navigation.launch.py namespace:=/rc
   ```

---

### 🦾 3. Arm Control (MoveIt 2)
To control the robotic arm manipulator via MoveIt 2:

1. **Start the Gazebo Simulation:**
   ```bash
   ros2 launch rc_gz simulation.launch.py
   ```
2. **Start MoveIt 2 configuration & controller managers:** (in a new terminal)
   ```bash
   ros2 launch rc_manipulators moveit.launch.py use_sim_time:=true
   ```
3. **Launch MoveIt RViz Visualizer:** (in a new terminal)
   ```bash
   ros2 launch rc_viz view_moveit.launch.py namespace:=rc use_sim_time:=True
   ```