cmake_minimum_required (VERSION 2.8.11)
project (tap)
set(CMAKE_CXX_STANDARD 14)
set(NAME "emp-sh2pc")

find_path(CMAKE_FOLDER NAMES cmake/emp-tool-config.cmake)
include(${CMAKE_FOLDER}/cmake/common.cmake)
include(${CMAKE_FOLDER}/cmake/source_of_randomness.cmake)
include(${CMAKE_FOLDER}/cmake/threading.cmake)

find_package(emp-ot REQUIRED)
include_directories(${EMP-OT_INCLUDE_DIRS})

# Test cases
macro (add_test _name)
    add_test_with_lib(${_name} ${EMP-OT_LIBRARIES})
endmacro()

#add_test (circuit)
add_test (client)
add_test (tap)
add_test (trigger)
add_test (action)
add_test (ot)
