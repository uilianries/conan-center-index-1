cmake_minimum_required(VERSION 3.1)
project(PackageTest C)

find_package(base64 REQUIRED)
add_executable(example example.c)
target_link_libraries(example base64::base64)
