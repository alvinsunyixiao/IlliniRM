project(PCL_EXAMPLE)
cmake_minimum_required(VERSION 2.8)
aux_source_directory(. SRC_LIST)
add_executable(${PROJECT_NAME} ${SRC_LIST})
set(CMAKE_PREFIX_PATH $ENV{HOME}/Qt/5.5/gcc_64)
 
find_package( PCL 1.7 REQUIRED )
find_package( Qt5 REQUIRED COMPONENTS Widgets Core )
 
include( CheckCXXCompilerFlag )
set( CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11" )
 
include_directories( ${PCL_INCLUDE_DIRS} /user/local/include )
link_directories( ${PCL_LIBRARY_DIRS} /usr/local/lib /usr/lib/x86_64-linux-gnu )
add_definitions( ${PCL_DEFINITIONS} )
 
target_link_libraries( PCL_EXAMPLE ${PCL_LIBRARIES} /usr/local/lib/librealsense.dylib)

