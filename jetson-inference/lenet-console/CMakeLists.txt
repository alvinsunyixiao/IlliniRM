file(GLOB lenetCameraSources *.cpp)
file(GLOB lenetCameraIncludes *.h )

cuda_add_executable(lenet-console ${lenetCameraSources})
target_link_libraries(lenet-console jetson-inference)
