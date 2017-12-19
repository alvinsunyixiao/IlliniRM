import cv2
import numpy as np
import num_recog
import time

_DEBUG = False

#TODO: Priority: 1-5
'''
- mask process
    - kernel: adjusted for 640*360 /Priority: 1
    - Time Optimization /Priority: 1
- filterRects
    - y / x: height/width ratio
- pre_process
    - kernel for GaussianBlur and Morphological transformation adjusted for 640*360 /Priority: 2
- pad_white_digit
    - 实验+微调 red digit height 的生成长宽比 /Priority: 2
- red_color_binarization
    - 阀值需要大调，调整至能够识别显示屏红和晶体管红。 /Priority: 4
- find_and_filter_contour
    - 面积阀值调整 /Priority: 3
- bound_red_number
    - y 阀值调整 /Priority: 1
'''
# Swap 2 objects
def swap(a,b):
    return b,a

def get_size(cv2_img):
    return (len(cv2_img[0]), len(cv2_img)) #width, height

def pad_diggit(img):
    w, h = img.shape[1], img.shape[0]
    length = int(h * 1.4)
    v_pad = int((length - h) / 2)
    h_pad = int((length - w) / 2)
    new_img = cv2.copyMakeBorder(img, v_pad, v_pad, h_pad, h_pad, borderType=cv2.BORDER_CONSTANT, value=0)
    #new_img = cv2.resize(new_img, (8, 8))
    return cv2.resize(new_img, (28,28))

'''
Sort a four-point arrary with respect to its relative spatial location

Output: [pt1, pt2, pt3, pt4]
Satifying the following spatial condition: |pt1 pt2|
                                           |pt3 pt4|
'''
def rank(dig_ids, contours_array):
    assert len(contours_array) == 9
    unranked_list = [[], [], []]
    for n in range(9):
        unranked_list[2 - (n / 3)].append([int(contours_array[n][0, 0]), int(contours_array[n][0, 1]), dig_ids[n]])
    ranked_list = [sorted(i, key = lambda x: x[0]) for i in unranked_list]
    ret = []
    for i in ranked_list:
        for j in i:
            ret.append(j[2])
    return ret

def mask_process(mask, points):
    kernel1 = np.ones((7,6),np.uint8)
    kernel2 = np.ones((6,6),np.uint8)
    kernel3 = np.ones((3,3),np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel2)

    y_min = min(points,key=lambda cnt: cnt[0,1])[0,1]
    y_min = int(y_min)
    x_min1 = min(points, key=lambda cnt: cnt[1,0])[1,0]
    x_min1 = int(x_min1)
    x_min2 = max(points, key=lambda cnt: cnt[0,0])[0,0]
    x_min2 = int(x_min2)
    ftr = np.ones(img.shape[0:2],np.uint8)
    ftr[y_min:-1,:] = 0
    ftr[:,0:x_min1] = 0
    ftr[:,x_min2:] = 0
    return cv2.bitwise_and(mask, mask, mask=ftr)

def sort_points(rect):
    x_sort = np.array(sorted(rect, key=lambda x: x[1]))
    if x_sort[0,0] > x_sort[1,0]:
        x_sort[0,0], x_sort[1,0] = swap(x_sort[0,0], x_sort[1,0])
    if x_sort[2,0] > x_sort[3,0]:
        x_sort[2,0], x_sort[3,0] = swap(x_sort[2,0], x_sort[3,0])
    return x_sort

def find_contour_bound(cont, raw_cont = False):
    if raw_cont: cont = cont[:,0]
    left_bound = min(cont, key = lambda x: x[0])[0]
    right_bound = max(cont, key = lambda x: x[0])[0]
    lower_bound = min(cont, key = lambda x: x[1])[1]
    upper_bound = max(cont, key = lambda x: x[1])[1]
    return (left_bound, right_bound, lower_bound, upper_bound)

# Load image and compute its threshold binary map

def filterRects(rect, pure_cont = False):
    if pure_cont:
        left_bound, right_bound, lower_bound, upper_bound = find_contour_bound(rect[:,0])
    else:
        left_bound, right_bound, lower_bound, upper_bound = find_contour_bound(rect)
    x = right_bound - left_bound
    y = float(upper_bound) - lower_bound
    print y / x
    if y / x >= 0.3 and y / x <= 0.75:
        return True
    return False

def pre_process(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7,7), 0)
    ret3, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    kernel = np.ones((4,8),np.uint8)
    return cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

def find_and_filter_contour(thresh):
    # Find all contours
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Filter out contours that are either too big or too small
    width, height = get_size(img)
    img_width_range = (0.125 * width, 0.3 * width)
    img_height_range = (0.1 * height, 0.18 * height)
    #contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= 100*40 and cv2.contourArea(cnt) <= 300*150]
    return [cnt for cnt in contours if cv2.contourArea(cnt) >= img_width_range[0] * img_height_range[0] and cv2.contourArea(cnt) <= img_width_range[1] * img_height_range[1] and filterRects(cnt, pure_cont = True)]

def four_poly_approx():
    tmp = []
    for cnt in contours:
        epsilon = 0.05 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            tmp.append(approx)
    #tmp = np.array(tmp)[:,:,0,:]
    return tmp

'''
Input:
    contours - processed contours
    gray - binirazied gray image
Output:
    bbox - lists of images of padded number
    digit_height - approximated red digit height
    points - points for contours
'''
def pad_white_digit(contours, gray):
    BOX_LEN = 32                # bounding box length for digits
    offset = (BOX_LEN - 28) / 2 # calculated padding length
    # Destination Points
    dstpts = np.array([[0,0],[BOX_LEN,0],[0,BOX_LEN],[BOX_LEN,BOX_LEN]], dtype='float32')

    bboxs = []
    points = []
    dynamic_height = []

    for cnt in contours:
        # Sort points with respect to relative location
        pts1 = sort_points(cnt).astype('float32')
        points.append(pts1)
        # Geometric transformation that project the 4-sided shape onto a 32x32 grid
        M = cv2.getPerspectiveTransform(pts1,dstpts)
        new_img = cv2.warpPerspective(gray,M,(BOX_LEN,BOX_LEN))
        new_img = 255 - new_img[offset:-offset, offset:-offset]
        bboxs.append(new_img)
        left, right, lower, upper = find_contour_bound(cnt)
        dynamic_height.append(int(upper - lower))

    digit_height = int(dynamic_height[len(dynamic_height) // 2] * (0.58))
    return np.array(bboxs)[:, None,...], digit_height, points

'''
Input:
    org_img - original unprocessed image
Output:
    mask - red-color-binarized image
'''
def red_color_binarization(org_img):
    hsv_img = cv2.cvtColor(org_img, cv2.COLOR_BGR2HSV)
    #lower_red = np.array([0,30,40])
    #upper_red = np.array([35,255,255])
    lower_red = np.array([0,4,210])
    upper_red = np.array([25,255,255])
    mask = cv2.inRange(hsv_img, lower_red, upper_red)
    mask1 = cv2.inRange(hsv_img, lower_red, upper_red)
    #lower_red = np.array([145,30,40])
    #upper_red = np.array([179,255,255])
    lower_red = np.array([155,4,210])
    upper_red = np.array([179,255,255])
    mask2 = cv2.inRange(hsv_img, lower_red, upper_red)
    return np.bitwise_or(mask1, mask2)

def bound_red_number(mask):
    im2, sct_cnts, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects = [cv2.boundingRect(cnt) for cnt in sct_cnts]
    rects = [rect for rect in rects if rect[2] < rect[3]]

    rects = sorted(rects, key=lambda x: x[0])
    y = sorted(rects, key=lambda x: x[1])
    y = y[len(y)/2][1]
    return [rect for rect in rects if rect[1] >= y * 0.8 and rect[1] <= y * 1.23]
