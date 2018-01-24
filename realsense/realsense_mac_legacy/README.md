# librealsense mac 安装指南

(librealsense legacy (implements a subset of librealsense2)；mac 只能用 legacy，librealsense 2 官方暂时无法支持 R200)

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
make
sudo make install
```

### Build librealsense

```
git clone https://github.com/IntelRealSense/librealsense
cd librealsense
git checkout legacy
mkdir build
cd build
cmake .. -DBUILD_EXAMPLES=ON
make
sudo make install
cpp-capture //run exmaple to test (need a live realsense camera connected to a USB 3.0 port; better with a powered hub)
```

### Setup Python wrapper

```
sudo pip install pyrealsense2
python -c "import pyrealsense; print 'hello'" #Confirm pyrealsense is successfully installed
```

## References and More Links (For Windows & Linux Users)
* [Official README](https://github.com/IntelRealSense/librealsense)
* [Official OSX Installtion Guide](https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_osx.md)
* [Official Linux Installation Guide](https://github.com/IntelRealSense/librealsense/blob/master/doc/installation.md)
* [Official Windows Installtion Guide](https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_windows.md)
* [Official Jetson TX2 Installtion Guide](https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_jetson.md)

- https://github.com/IntelRealSense/librealsense/issues/729
- https://gist.github.com/svenevs/f00ed3898d2af6248921b63254aa8cc1
- https://github.com/IntelRealSense/librealsense/issues/436
