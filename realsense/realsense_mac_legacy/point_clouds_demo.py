import logging
logging.basicConfig(level=logging.INFO)

import time
import numpy as np
import cv2
import pyrealsense as pyrs
from pyrealsense.constants import rs_option
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

depth_fps = 90
depth_stream = pyrs.stream.DepthStream(fps=depth_fps)

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

def convert_z16_to_bgr(frame):
    '''Performs depth histogram normalization

    This raw Python implementation is slow. See here for a fast implementation using Cython:
    https://github.com/pupil-labs/pupil/blob/master/pupil_src/shared_modules/cython_methods/methods.pyx
    '''
    hist = np.histogram(frame, bins=0x10000)[0]
    hist = np.cumsum(hist)
    hist -= hist[0]
    rgb_frame = np.empty(frame.shape[:2] + (3,), dtype=np.uint8)

    zeros = frame == 0
    non_zeros = frame != 0

    f = hist[frame[non_zeros]] * 255 / hist[0xFFFF]
    rgb_frame[non_zeros, 0] = 255 - f
    rgb_frame[non_zeros, 1] = 0
    rgb_frame[non_zeros, 2] = f
    rgb_frame[zeros, 0] = 20
    rgb_frame[zeros, 1] = 5
    rgb_frame[zeros, 2] = 0
    return rgb_frame


with pyrs.Service() as serv:
    with serv.Device(streams=(depth_stream,)) as dev:

        dev.apply_ivcam_preset(0)

        try:  # set custom gain/exposure values to obtain good depth image
            custom_options = [(rs_option.RS_OPTION_R200_LR_EXPOSURE, 30.0),
                              (rs_option.RS_OPTION_R200_LR_GAIN, 100.0)]
            dev.set_device_options(*zip(*custom_options))
        except pyrs.RealsenseError:
            pass  # options are not available on all devices

        cnt = 0
        last = time.time()
        smoothing = 0.9
        fps_smooth = depth_fps

        for i in range(1):

            cnt += 1
            if (cnt % 30) == 0:
                now = time.time()
                dt = now - last
                fps = 30/dt
                fps_smooth = (fps_smooth * smoothing) + (fps * (1.0-smoothing))
                last = now

            dev.wait_for_frames()
            d = dev.depth
            x_vec, y_vec, z_vec = point_cloud(d)
            print("printing len \n")
            print(len(x_vec))
            print(len(y_vec))
            print(len(z_vec))
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(x_vec, y_vec, z_vec)
            plt.show()
            plt.pause(20)
            #d = convert_z16_to_bgr(d)

            #cv2.putText(d, str(fps_smooth)[:4], (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255))

            #cv2.imshow('', d)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break
