cmake_minimum_required(VERSION 3.14)
project(rc_common)
find_package(ament_cmake REQUIRED)
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME})
ament_package()
