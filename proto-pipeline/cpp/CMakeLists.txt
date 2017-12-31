cmake_minimum_required(VERSION 2.8)
project(grid-detect)
set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake)
find_package(Caffe REQUIRED)
add_executable(grid-detect grid-detect.cpp)

include_directories(${Caffe_INCLUDE_DIRS})
target_link_libraries(grid-detect ${Caffe_LIBRARIES} )
