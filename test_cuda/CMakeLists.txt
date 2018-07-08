cmake_minimum_required(VERSION 2.8)
project(TESTCUDA)

set(CMAKE_EXPORT_COMPILE_COMMANDS 1)

add_compile_options(-std=c++11)
add_compile_options(-g)

find_package(OpenCV REQUIRED)

include_directories(${OpenCV_INLUCDE_DIRS})

find_package(CUDA REQUIRED)
include_directories(${CUDA_INCLUDE_DIRS})

add_executable(test_cuda ./test_cuda.cpp)
target_link_libraries(test_cuda ${OpenCV_LIBS})
