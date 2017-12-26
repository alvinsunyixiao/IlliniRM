# librealsense mac 安装指南
# 暂时还不能够 work（include 没修好；需要添加 c++11 flag），等搞定了再更新

## Prerequisites
* [Homebrew](https://brew.sh/)
* Python (Recommend to use python2 installed from [Homebrew](https://brew.sh/): `brew install python2`)

## Installing librealsense on Mac

### Dependencies

```
brew install libuvc libusb
git clone https://github.com/glfw/glfw.git
cd glfw/
git checkout latest
mkdir build
cd build
cmake .. -DBUILD_SHARED_LIBS=ON
make -j4
sudo make install
brew install llvm
```

### Build librealsense

```
git clone https://github.com/IntelRealSense/librealsense
cd librealsense
mkdir build
cd build
//one-time setting that compiles with OpenMP features
export CPPFLAGS="-I/usr/local/opt/llvm/include"
export LDFLAGS="-L/usr/local/opt/llvm/lib"
export CXX=/usr/local/opt/llvm/bin/clang++
export CC=/usr/local/opt/llvm/bin/clang
cmake .. -DBUILD_EXAMPLES=ON -DBUILD_PYTHON_BINDINGS=bool:true -DBUILD_CV_EXAMPLES=true //可能需要 -DBUILD_WITH_OPENMP=false
make -j4
sudo make install
```

### Setup PYTHONPATH
### Manually Fixing Include

## References and More Links (For Windows & Linux Users)
* [Official README](https://github.com/IntelRealSense/librealsense)
* [Official OSX Installtion Guide](https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_osx.md)
* [Official Linux Installation Guide](https://github.com/IntelRealSense/librealsense/blob/master/doc/installation.md)
* [Official Windows Installtion Guide](https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_windows.md)
* [Official Jetson TX2 Installtion Guide](https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_jetson.md)

- https://github.com/IntelRealSense/librealsense/issues/729
- https://gist.github.com/svenevs/f00ed3898d2af6248921b63254aa8cc1
- https://github.com/IntelRealSense/librealsense/issues/436
