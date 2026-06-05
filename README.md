# RC MMR Simulation & Controls (`rc_mmr_sim`)

This repository contains the simulation overlay packages for the **A300 Mobile Manipulator Robot (MMR)**. It provides complete integration with **Webots Simulation**, **Nav2 Navigation**, **SLAM**, and **MoveIt 2** for manipulator control, built on top of standard ROS 2 (Jazzy Jalisco).

> [!NOTE]
> This repository is a sub-module/component of the main development workspace repository:
> [rc-robocup Dev Environment](https://github.com/Adyansh04/rc-robocup)
>
> 📖 For details on simulation internals, modifications, and architecture, see the [**Webots Simulation Architecture Guide**](./docs/simulation_architecture.md).

---

## 📦 Package Directory

Here is the list of ROS 2 packages included in this repository:

| Package | Description |
|---|---|
| [**`rc_common`**](./rc_common) | Dynamic package-share config tracker. Holds robot parameters (`robot.yaml`), configurations (`robot.urdf.xacro`, `robot.srdf`), and unified launch files. |
| [**`rc_control`**](./rc_control) | Platform teleoperation controls, joystick support, and base localization. |
| [**`rc_manipulators`**](./rc_manipulators) | MoveIt 2 configuration, launch scripts, and controller managers for the arm manipulator. |
| [**`rc_manipulators_description`**](./rc_manipulators_description) | URDF / Xacro description files specific to the arm manipulator. |
| [**`rc_nav2_demos`**](./rc_nav2_demos) | Nav2 stack configuration, path planning, slam maps, and navigation scripts. |
| [**`rc_platform_description`**](./rc_platform_description) | URDF / Xacro description files specific to the A300 mobile base platform. |
| [**`rc_sensors_description`**](./rc_sensors_description) | URDF / Xacro description files for LiDAR, camera, and IMU sensors. |
| [**`rc_viz`**](./rc_viz) | Rviz2 pre-configured layouts and visualization launching scripts. |
| [**`rc_webots`**](./rc_webots) | Webots simulation setup, containing world definitions, spawners, and controllers. |

---

## 🚀 Running the Demos

> [!IMPORTANT]
> Make sure you are running these commands inside your active ROS 2 container (`ros2_dev_jazzy`).
> Before running any commands, build the workspace and source the setup files:
> ```bash
> cd /root/workspace
> colcon build --symlink-install
> source install/setup.bash
> ```

### 🗺️ 1. Mapping & SLAM (gmapping)
Use this command to launch the Webots simulator, Nav2, SLAM mapping stack, and RViz navigation visualization.

1. **Launch Mapping Stack:**
   ```bash
   ros2 launch rc_common robot.launch.py mapping:=true teleop:=true
   ```
   *Passing `teleop:=true` will automatically open `teleop_twist_keyboard` inside a new terminal window.*

2. **Alternatively, manually launch Keyboard Teleoperation:** (if not using `teleop:=true`)
   ```bash
   ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/rc/platform_velocity_controller/cmd_vel -p stamped:=true
   ```
3. **Save the Map:**
   When you are satisfied with the mapped area, run the following command to save it (the saved map files `my_map.yaml` and `my_map.pgm` will be generated in your current working directory):
   ```bash
   ros2 run nav2_map_server map_saver_cli -f "my_map" --ros-args -p map_subscribe_transient_local:=true -r __ns:=/rc
   ```

---

### 🧭 2. Autonomous Navigation & Arm Control (Nav2 + MoveIt)
Once you have a saved map, you can run navigation with localization alongside MoveIt 2 arm control.

1. **Launch Simulation, Navigation, MoveIt & RViz:**
   ```bash
   ros2 launch rc_common robot.launch.py
   ```
   *By default, this launches navigation with `my_map.yaml`, MoveIt 2 arm control, and both RViz visualizer windows.*

2. **Arguments for custom launch configurations:**
   - `nav2:=false`: Disable the Nav2 navigation stack.
   - `moveit:=false`: Disable the MoveIt arm control stack.
   - `rviz:=false`: Disable launching the RViz visualizers.
   - `teleop:=true`: Automatically open the teleop twist keyboard in a new terminal window.
   - `map:=/path/to/map.yaml`: Specify a different map file.