#!/usr/bin/env python
import cv2
import numpy as np
import time
from IPython import embed

baseline_mean = [150, 210, 230]
baseline_std = [50, 40 ,25]

def naive_test(query, baseline, threshold):
    assert(len(query) == len(baseline))
    for i in range(len(baseline)):
        if(abs(query[i] - baseline[i]) > threshold):
            return False
    return True

def get_contour_stats(single_contour, img):
    channels = []
    for i in range(3):
        channels.append(img[:,:,i])
    mask = np.zeros(channels[0].shape, dtype = "uint8")
    cv2.drawContours(mask, [single_contour], -1, 255, -1)
    my_mean = []
    my_std = []
    for channel in channels:
        _mean, _stddev = cv2.meanStdDev(channel, mask = mask)
        my_mean.append(int(_mean[0, 0]))
        my_std.append(int(_stddev[0, 0]))
    return (my_mean, my_std)

#def stupid_put_text(img, text, point_x, point_y):

cap = cv2.VideoCapture('./fire.mp4')
while cap.isOpened():
    ret, img = cap.read()
    img = cv2.resize(img, (640, 360))
    if not ret: break
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #gray = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh_num, ret_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, pre_contours, hierarchy = cv2.findContours(ret_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = []
    '''
    for ctr in pre_contours:
        area_s = cv2.contourArea(ctr)
        cv2.putText(img, str(area_s),
                    (int(ctr[0, 0, 0]), int(ctr[0, 0, 1])),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                   (0,255,255),
                   2,cv2.LINE_AA)
    '''
    for ctr in pre_contours:
        area_size = cv2.contourArea(ctr)
        if area_size > 400 and area_size < 4000: #25 * 25
            contours.append(ctr)
    print(len(contours))
    post_contours = []
    stats = []

    mask_debug = np.zeros(gray.shape, dtype = "uint8")
    for ctr in contours:
        cv2.drawContours(mask_debug, [ctr], -1, 255, -1)
    cv2.imshow("debug", mask_debug)
    cv2.waitKey(1)

    for ctr in contours:
        cur_mean, cur_std = get_contour_stats(ctr, img)
        if naive_test(cur_mean, baseline_mean, 55) and naive_test(cur_std, baseline_std, 20):
            post_contours.append(ctr)
            stats.append((ctr[0][0], str(cur_mean), str(cur_std)))
    for stat in stats:
        cv2.putText(img, stat[2],
                    (int(stat[0][0]), int(stat[0][1])),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                   (0,255,255),
                   2,cv2.LINE_AA)
    cv2.drawContours(img, post_contours, -1, (255, 0, 0), 3)
    cv2.imshow("test", img)
    cv2.waitKey(1)

cap.release()
