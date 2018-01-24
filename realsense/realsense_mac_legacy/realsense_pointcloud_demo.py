#!/usr/bin/env python3
import pyrealsense as pyrs
from pyrealsense.constants import rs_option
import time
import matplotlib.pyplot as plt

def point_cloud(depth, cx=320.0, cy=240.0, fx=463.889, fy=463.889):
    """Transform a depth image into a point cloud with one point for each
    pixel in the image, using the camera transform for a camera
    centred at cx, cy with field of view fx, fy.

    depth is a 2-D ndarray with shape (rows, cols) containing
    depths from 1 to 254 inclusive. The result is a 3-D array with
    shape (rows, cols, 3). Pixels with invalid depth in the input have
    NaN for the z-coordinate in the result.

    My Changes:
        * Author had divided depth by 256 to normalize, I hadn't done that so I removed it.
        * Output coordinates are in units of 1m. There is a factor of 500 applied at image capture.
        * Author had returned a 3 * 480 * 640 np array. I changed to 3 flat arrays
    """
    rows, cols = depth.shape
    print(fx, fy, cx, cy)
    c, r = np.meshgrid(np.arange(cols), np.arange(rows), sparse=True)
    valid = (depth >= 0) & (depth <= 255)
    z = np.where(valid, depth, np.nan)
    x = np.where(valid, z * (c - cx) / fx, 0)
    y = np.where(valid, z * (r - cy) / fy, 0)
    return x.flatten(), y.flatten(), z.flatten()

def convert_z16_to_rgb(frame):
    '''Python implementation of librealsense make_depth_histogram()

    See source code:
    https://github.com/IntelRealSense/librealsense/blob/master/examples/example.hpp#L10-L33
    '''

    # calculate depth histogram
    hist, edges = np.histogram(frame, bins=0x10000)
    plt.figure(figsize=(16, 4))
    plt.subplot(1, 2, 1)
    plt.scatter(edges[:-1], hist, s=1)
    plt.title('Depth histogram')

    # calculate cumulative depth histogram
    hist = np.cumsum(hist)
    hist -= hist[0]
    plt.subplot(1, 2, 2)
    plt.scatter(edges[:-1], hist, s=1)
    plt.title('Cumulative depth histogram')
    plt.tight_layout()
    rgb_frame = np.zeros(frame.shape[:2] + (3,), dtype=np.uint8)

    zeros = frame==0
    non_zeros = frame!=0

    f = hist[frame[non_zeros]] * 255 / hist[0xFFFF]
    rgb_frame[non_zeros, 0] = f
    rgb_frame[non_zeros, 1] = 0
    rgb_frame[non_zeros, 2] = 255 - f
    rgb_frame[zeros, 0] = 0
    rgb_frame[zeros, 1] = 5
    rgb_frame[zeros, 2] = 20
    return rgb_frame

#print available devices
with pyrs.Service() as serv:
    for dev in serv.get_devices():
        print(dev)

def main():
    with pyrs.Service() as serv:
        depth_fps = 90
        depth_stream = pyrs.stream.DepthStream(fps=depth_fps)
        with serv.Device(streams=(depth_stream,)) as dev:
            dev.apply_ivcam_preset(0)

            try:  # set custom gain/exposure values to obtain good depth image
                custom_options = [(rs_option.RS_OPTION_R200_LR_EXPOSURE, 30.0),
                                  (rs_option.RS_OPTION_R200_LR_GAIN, 100.0)]
                dev.set_device_options(*zip(*custom_options))
            except pyrs.RealsenseError:
                pass  # options are not available on all devices

            time.sleep(1) #wait for the device to initialize
        while True:
            dev.wait_for_frames()
            frame = dev.depth
            plt.imshow(frame)
            plt.show()
            plt.pause(0.01)

if __name__ == '__main__':
    main()
