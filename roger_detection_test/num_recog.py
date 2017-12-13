import cv2
import math
import matplotlib.pyplot as plt

one_threshold = 170

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

def digit_recognition(padded_num):
    if padded_num.mean() >= one_threshold:
        return 1
    u_x, u_y, width, height = cv2.boundingRect(padded_num)
    print u_x, u_y, width, height
    on = [0 for i in range(7)]
    tube_width, tube_height = int(width * 0.25), int(height * 0.18)
    bias = int(height * 0.09)
    segments = [
        ((u_x, u_y + bias), (u_x + tube_width, u_y + height // 2)),	# top-left
        ((u_x, u_y + height // 2 - bias), (u_x + tube_width, u_y + height - bias)),	# bottom-left
        ((u_x + width - tube_width, u_y), (u_x + width, u_y + height // 2)),	# top-right
        ((u_x + width - tube_width, u_y + height // 2), (u_x + width, u_y + height - bias)),	# bottom-right
        ((u_x + tube_width, u_y), (u_x + width - tube_width, u_y + tube_height)),	# top
        ((u_x + tube_width, u_y + (height // 2) - bias) , (u_x + width - tube_width, u_y + (height // 2) + bias)), # center
        ((u_x + tube_width, u_y + height - tube_height), (u_x + width - tube_width, u_y + height))	# bottom
    ]
    plt.imshow(padded_num)
    for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
        print "Current " + str(((xA, yA), (xB, yB)))
        segment = padded_num[yA:yB, xA:xB]
        total = cv2.countNonZero(segment)
        area = (xB - xA) * (yB - yA)
        print "Current Area Protion" + str(total / float(area))
        if total / float(area) > 0.68: on[i]= 1
        if i == 0:
            plt.axhline(y = yA, color = 'blue')
            plt.axhline(y = yB, color = 'blue')
            plt.axvline(x = xA, color = 'red')
            plt.axvline(x = xB, color = 'red')
    plt.show()
    print on
    try:
        return digit_match[tuple(on)]
    except KeyError:
        return False