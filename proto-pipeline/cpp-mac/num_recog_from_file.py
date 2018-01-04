import cv2
import math
import matplotlib.pyplot as plt
import numpy as np
import sys

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

def remove_smear(img, x, y, width, height):
    #print x,y,width,height
    #if x >= width - 7 or y >= height - 7: return None
    if x == width or y == height: return np.array([])
    left_col = cv2.countNonZero(img[:,x:x+1])
    if _DEBUG:
        print "left", left_col
    if left_col <= 3: #lower because it could be 7
        return remove_smear(img, x + 1, y, width, height)
    right_col = cv2.countNonZero(img[:,x+width-1:x+width])
    if _DEBUG:
        print "right", right_col
    if right_col <= 5: return remove_smear(img, x, y, width - 1, height)
    upper_row = cv2.countNonZero(img[y:y+1])
    if _DEBUG:
        print "upper", upper_row
    if upper_row <= 4: return remove_smear(img, x, y + 1, width, height)
    lower_row = cv2.countNonZero(img[y+height-1:y+height])
    if _DEBUG:
        print "lower", lower_row
    if lower_row <= 4: return remove_smear(img, x, y, width, height - 1)
    return img[y:y+height, x:x+width]

def digit_recognition(padded_num, tilt_offset = 1, on = None):
    if not on:
        on = [0 for i in range(7)]
    if padded_num.mean() >= one_threshold:
        return 1
    thresh_value, padded_num = cv2.threshold(padded_num, 240, 255, cv2.THRESH_BINARY)
    u_x, u_y, width, height = cv2.boundingRect(padded_num)
    if width < 8: #too slim
        return 1
    padded_num = remove_smear(padded_num, u_x, u_y, width, height)
    if not padded_num.any():
        if _DEBUG:
            print "Wadu hek"
        return -1
    #print u_x, u_y, width, height
    #tube_width, tube_height = int(width * 0.25), int(height * 0.18)
    #tube_width = int((width * 0.25 + height * 0.18) / 2)
    u_x, u_y, width, height = cv2.boundingRect(padded_num)
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
            if total / float(area) >= 0.5:
                on[i]= 1
        except ZeroDivisionError:
            print "Warning: Zero division! Returning 1 as result (could be inaccurate)..."
            return 1
        if _DEBUG:
            if i == 2:
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

def main(cur_num):
    img = cv2.imread("/tmp/" + str(cur_num) + "_temp.jpg", 0) #load img in grayscale
    return digit_recognition(img)

if __name__ == '__main__' and len(sys.argv) >= 2:
    resu = []
    for i in range(int(sys.argv[1])):
        resu.append(main(i))
    for i in resu:
        print i
