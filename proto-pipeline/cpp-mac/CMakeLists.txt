cmake_minimum_required(VERSION 2.8)
project(grid-detect)
set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake)

find_package(Caffe REQUIRED)
find_package(OpenCV REQUIRED)

include_directories(${Caffe_INCLUDE_DIRS})
include_directories(${OpenCV_INLUCDE_DIRS})
include_directories(/usr/local/cuda-9.0/include)

add_executable(grid-detect grid-detect.cpp)

target_link_libraries(grid-detect ${Caffe_LIBRARIES} ${OpenCV_LIBS} glog boost_system)
