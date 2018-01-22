import cv2
import numpy as np

one_threshold = 230
on_threshold = 9

digit_match = {
	(1, 1, 1, 1, 1, 0, 1): 0,
	(0, 0, 1, 1, 0, 0, 0): 1,
	(0, 1, 1, 0, 1, 1, 1): 2,
	(0, 0, 1, 1, 1, 1, 1): 3,
	(1, 0, 1, 1, 0, 1, 0): 4,
	(1, 0, 0, 1, 1, 1, 1): 5,
	(1, 1, 0, 1, 1, 1, 1): 6,
	(0, 0, 1, 1, 1, 0, 0): 7,
	(1, 1, 1, 1, 1, 1, 1): 8,
	(1, 0, 1, 1, 1, 1, 1): 9
}

segments = [[0, 3, 3, 4],
            [0, 11, 3, 4],
            [7, 3, 3, 4],
            [7, 11, 3, 4],
            [4, 0, 3, 4],
            [4, 7, 3, 4],
            [4, 14, 3, 4]]

def digit_recognition(img):
    if img.shape[0] < 8: return 1 #too slim
    thresh_value, temp_thresh = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY)
    if img.mean() > one_threshold: return 1 #too bright
    u_x, u_y, width, height = cv2.boundingRect(temp_thresh)
    img = img[u_y:u_y + height, u_x:u_x + width]
    cv2.imwrite("debug_3.jpg", img)
    img = cv2.resize(img, (10, 18), 0, 0, cv2.INTER_NEAREST)
    cv2.imwrite("debug_2.jpg", img)
    on_test = [0 for i in range(7)]
    for i in range(7):
        cur_seg_pixel = cv2.countNonZero(img[segments[i][1]:segments[i][1] + segments[i][3], segments[i][0]:segments[i][0] + segments[i][2]])
        if cur_seg_pixel > on_threshold: on_test[i] = 1
    try:
        return digit_match[tuple(on_test)]
    except KeyError:
        return -1
