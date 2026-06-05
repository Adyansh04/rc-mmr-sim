import os
files = [
  '/root/workspace/src/rc_mmr_sim/rc_manipulators_description/urdf/arm/ur_description_webots/urdf/ur.urdf.xacro',
  '/root/workspace/src/rc_mmr_sim/rc_manipulators_description/urdf/arm/ur_description_webots/urdf/ur_macro.xacro',
  '/root/workspace/src/rc_mmr_sim/rc_manipulators_description/urdf/arm/ur_description_webots/config/ur5e/visual_parameters.yaml'
]

for f in files:
    with open(f, 'r') as file:
        content = file.read()
    
    # We must replace both $(find ...) formats since bash interpreted them earlier
    content = content.replace('$(find webots_ros2_universal_robot)/resource/Universal_Robots_ROS2_Driver/ur_description', '$(find rc_manipulators_description)/urdf/arm/ur_description_webots')
    content = content.replace('$(find webots_ros2_universal_robot)//resource/Universal_Robots_ROS2_Driver/ur_description', '$(find rc_manipulators_description)/urdf/arm/ur_description_webots')
    content = content.replace('package://webots_ros2_universal_robot/resource/Universal_Robots_ROS2_Driver/ur_description', 'package://rc_manipulators_description/urdf/arm/ur_description_webots')
    
    with open(f, 'w') as file:
        file.write(content)
print('Done replacing paths!')
