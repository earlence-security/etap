cmake_minimum_required(VERSION 3.10)
project(dtap_lib)

set(CMAKE_CXX_STANDARD 14)

find_path(CMAKE_FOLDER NAMES cmake/emp-tool-config.cmake)
include(${CMAKE_FOLDER}/cmake/common.cmake)
include(${CMAKE_FOLDER}/cmake/source_of_randomness.cmake)
include(${CMAKE_FOLDER}/cmake/threading.cmake)

find_package(emp-tool REQUIRED)
include_directories(${EMP-TOOL_INCLUDE_DIRS})

find_package(pybind11 REQUIRED)
pybind11_add_module(dtap_lib trigger.cpp)
target_link_libraries(dtap_lib PRIVATE ${EMP-TOOL_LIBRARIES})
