cmake_minimum_required(VERSION 3.14)
project(rc_gz)
find_package(ament_cmake REQUIRED)

install(DIRECTORY
  config
  worlds
  meshes
  launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
