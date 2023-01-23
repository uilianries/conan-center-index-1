cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

set(CMAKE_VERBOSE_MAKEFILE ON)

find_package(FLEX CONFIG REQUIRED)
flex_target(flex_scanner basic_nr.l ${PROJECT_BINARY_DIR}/basic_nr.cpp)

add_executable(${PROJECT_NAME} basic_nr.cpp)
target_include_directories(${PROJECT_NAME} PRIVATE ${FLEX_INCLUDE_DIRS})
target_link_libraries(${PROJECT_NAME} PRIVATE ${FLEX_LIBRARIES})
