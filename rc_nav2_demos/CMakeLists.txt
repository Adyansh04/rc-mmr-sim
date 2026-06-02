cmake_minimum_required(VERSION 3.14)
project(rc_nav2_demos)
find_package(ament_cmake REQUIRED)
install(DIRECTORY launch config maps
  DESTINATION share/${PROJECT_NAME})
ament_package()
