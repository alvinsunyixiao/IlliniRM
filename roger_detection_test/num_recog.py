import cv2
import math
import matplotlib.pyplot as plt

one_threshold = 170
_DEBUG = False

"""
u_x  c2        c3    u_x + width
       -------        uy
      |   4   |
 ---   -------   ---  r2
|   |           |   |
| 0 |           | 2 |
|   |           |   |
 ---   -------   ---  r3
      |   5   |
 ---   -------   ---  r4
|   |           |   |
| 1 |           | 3 |
|   |           |   |
 ---   -------   ---  r5
      |   6   |
       -------        u_y + height
"""

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

def digit_recognition(padded_num, tilt_offset = 1, on = None):
    if not on:
        on = [0 for i in range(7)]
    if padded_num.mean() >= one_threshold:
        return 1
    thresh_value, padded_num = cv2.threshold(padded_num, 240, 255, cv2.THRESH_BINARY)
    u_x, u_y, width, height = cv2.boundingRect(padded_num)
    if width < 8: #too slim
        return 1
    #print u_x, u_y, width, height
    #tube_width, tube_height = int(width * 0.25), int(height * 0.18)
    #tube_width = int((width * 0.25 + height * 0.18) / 2)
    tube_width = 2
    tube_height = tube_width
    bias = int(height * 0.08)
    segments = [
        ((u_x + tilt_offset, u_y + tube_height), (u_x + tube_width + tilt_offset, u_y + height // 2 - tube_height)),	# top-left
        ((u_x + tilt_offset, u_y + height // 2 + bias), (u_x + tube_width + tilt_offset, u_y + height - tube_width - 1)),	# bottom-left
        ((u_x + width - tube_width, u_y + tube_height), (u_x + width - bias, u_y + height // 2 - tube_height)),	# top-right
        ((u_x + width - tube_width, u_y + height // 2 + bias), (u_x + width - bias, u_y + height - tube_width)),	# bottom-right
        ((u_x + tube_width, u_y), (u_x + width - tube_width - 1, u_y + tube_height - bias)),	# top
        ((u_x + tube_width, u_y + (height // 2)) , (u_x + width - tube_width, u_y + (height // 2) + bias)), # center
        ((u_x + tube_width, u_y + height - tube_height), (u_x + width - tube_width, u_y + height))	# bottom
    ]
    if _DEBUG:
        plt.imshow(padded_num)
    for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
        if _DEBUG:
            print "Current " + str(((xA, yA), (xB, yB)))
        segment = padded_num[yA:yB, xA:xB]
        total = cv2.countNonZero(segment)
        try:
            area = (xB - xA) * (yB - yA)
            if _DEBUG:
                print "Current Area Protion" + str(total / float(area))
            if total / float(area) >= 0.69:
                on[i]= 1
        except ZeroDivisionError:
            print "Warning: Zero division! Returning 1 as result (could be inaccurate)..."
            return 1
        if _DEBUG:
            if i == 0:
                plt.axhline(y = yA, color = 'blue')
                plt.axhline(y = yB, color = 'blue')
                plt.axvline(x = xA, color = 'red')
                plt.axvline(x = xB, color = 'red')
    if _DEBUG:
        plt.show()
        print on
    try:
        return digit_match[tuple(on)]
    except KeyError:
        if tilt_offset == -2: return -1
        return digit_recognition(padded_num, tilt_offset - 1, on)
