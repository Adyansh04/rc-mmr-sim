cmake_minimum_required(VERSION 3.14)
project(rc_manipulators_description)
find_package(ament_cmake REQUIRED)

install(DIRECTORY
  urdf
  srdf
  config
  meshes
  launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
