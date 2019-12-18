cmake_minimum_required(VERSION 2.8.12)
PROJECT(conancmakewrapper)

set(CMAKE_VERBOSE_MAKEFILE ON)

include("conanbuildinfo.cmake")
CONAN_BASIC_SETUP()

add_subdirectory("source_subfolder")
