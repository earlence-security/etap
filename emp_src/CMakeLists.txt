cmake_minimum_required(VERSION 3.10)
project(example_rules)

set(CMAKE_CXX_STANDARD 17)

find_path(CMAKE_FOLDER NAMES cmake/emp-tool-config.cmake)
include(${CMAKE_FOLDER}/cmake/common.cmake)
include(${CMAKE_FOLDER}/cmake/source_of_randomness.cmake)
include(${CMAKE_FOLDER}/cmake/threading.cmake)

find_package(emp-tool REQUIRED)
include_directories(${EMP-TOOL_INCLUDE_DIRS})

# Test cases
macro (add_test _name)
    add_test_with_lib(${_name} ${EMP-TOOL_LIBRARIES})
endmacro()

add_test (client)
add_test (trigger)
add_test (action)
add_test (tap)
add_test (func_reader)
