cmake_minimum_required(VERSION 3.14)
project(rc_common)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch platform sensors manipulators
  DESTINATION share/${PROJECT_NAME})

install(FILES robot.yaml robot.urdf.xacro robot.srdf robot.srdf.xacro
  DESTINATION share/${PROJECT_NAME})

ament_package()
