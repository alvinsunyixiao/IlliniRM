# coding: utf-8
# Load Neccessary Libraries
import caffe
import cv2
import numpy as np
import time
import num_recog
from collections import Counter

start_time = time.time()
_DEBUG = True
RED_RECORD_PATH = "/tmp/red_record.txt"
# Load caffe model
caffe.set_mode_cpu()

net = caffe.Net('./model/lenet.prototxt',
                './model/mnist_iter_200000.caffemodel',
               caffe.TEST)

red_number_record = [[] for i in range(5)]
white_number_record = [[] for i in range(9)]

def read_record(RED_RECORD_PATH):
    try:
        f = open(RED_RECORD_PATH)
        a = f.read()
        f.close()
        a = a.split('\n')
        prv_seq = a[0].split('|')[:-1]
        return [int(i) for i in prv_seq], int(a[1])
    except IOError:
        return None, None

'''
---------
Read record from saved file
---------
'''

prv_red_seq, prv_hit_round = read_record(RED_RECORD_PATH)
if prv_hit_round == 4: #WE HAD FINISHED ALL BEFORE
    prv_red_seq = None
    prv_hit_round = None

def write_record(seq_2_write, trial_num):
    global RED_RECORD_PATH
    f = open(RED_RECORD_PATH, "w")
    line1 = ""
    for i in seq_2_write:
        line1 += str(i) + "|"
    f.write(line1)
    f.write('\n')
    f.write(str(trial_num))
    f.close()

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
    if y / x >= 0.3 and y / x <= 0.6:
        return True
    return False

def update_record(input_sequence = None, red_number_sequence = None):
    global white_number_record
    global red_number_record
    if input_sequence:
        assert len(input_sequence) == 9
        for n in range(9):
            white_number_record[n].append(input_sequence[n])
    if red_number_sequence:
        assert len(red_number_sequence) == 5
        for n in range(5):
            red_number_record[n].append(red_number_sequence[n])

def calculate_position_2_hit(prv_red_seq, prv_hit_round):
    global white_number_record
    global red_number_record
    if len(white_number_record[0]) == 0 or len(red_number_record[0]) == 0:
        print "YOU RECOGNIZED NOTHING!!! SHAME ON YOU!!!"
        return -1
    final_white_seq = []
    for i in range(9):
        final_white_seq.append(Counter(white_number_record[i]).most_common(1)[0][0])
    final_red_seq = []
    for i in range(5):
        final_red_seq.append(Counter(red_number_record[i]).most_common(1)[0][0])
    if not prv_red_seq and not prv_hit_round: #New round
        cur_round = 0
    elif final_red_seq == prv_red_seq: #Had it correct; continue to next round
        cur_round = prv_hit_round + 1
    else: #Had it wrong; let's have a new start
        cur_round = 0
    write_record(final_red_seq, cur_round)
    return final_white_seq.index(final_red_seq[cur_round])

def process(img):
    global red_number_record
    global white_number_record
    #img = cv2.resize(img, (800,600))
    img_cp = img.copy()
    '''
    -------------
    Binarization and mark rects
    -------------
    '''
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7,7), 0)
    ret3,thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    # Find all contours
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Filter out contours that are either too big or too small
    width, height = get_size(img)
    img_width_range = (0.125 * width, 0.3 * width)
    img_height_range = (0.1 * height, 0.18 * height)
    #contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= 100*40 and cv2.contourArea(cnt) <= 300*150]
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= img_width_range[0] * img_height_range[0] and cv2.contourArea(cnt) <= img_width_range[1] * img_height_range[1] and filterRects(cnt, pure_cont = True)]
    # Find contour approximation and enforce a 4-sided convex shape
    tmp = []
    for cnt in contours:
        epsilon = 0.05 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt,epsilon,True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            tmp.append(approx)

    if len(tmp) == 0:
        return 0

    if _DEBUG:
        print "this is len of contours " + str(len(contours))
        print "This one is tmp " + str(len(tmp))
    if len(tmp) == 8:
        if _DEBUG:
            print "Manually fixing..."
        tmp = []
        for cnt in contours:
            left, right, lower, upper = find_contour_bound(cnt[:,0])
            box = [[left, lower], [right, lower], [right, upper], [left, upper]]
            tmp.append(box)
        while len(tmp) > 9:
            tmp.remove(max(tmp, key = lambda x: x[2][1])) #remove highest contour
        contours = np.array(tmp)
    else:
        contours = np.array(tmp)[:,:,0,:]

    cv2.drawContours(img, contours, -1, (0,255,0), 3)

    '''
    -------------
    format numbers in rects and pour into neural network
    -------------
    '''

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

    bboxs = np.array(bboxs)[:, None,...]

    net.blobs['data'].reshape(bboxs.shape[0], 1, 28, 28)
    net.blobs['data'].data[...] = bboxs.astype('float32') / 255
    out = net.forward()
    dig_ids = out['prob'].argmax(axis = 1)

    '''
    -------------
    Update output sequence for data set
    -------------
    '''
    if len(contours) == 9:
        output_sequence = rank(dig_ids, contours)
        update_record(input_sequence = output_sequence)
        if _DEBUG:
            print "White: " + str(output_sequence)

    '''
    -------------
    mask all color except red
    -------------
    '''

    org_img = img_cp.copy()
    hsv_img = cv2.cvtColor(org_img, cv2.COLOR_BGR2HSV)
    #lower_red = np.array([0,90,70])
    #upper_red = np.array([15,255,255])
    lower_red = np.array([0,30,40])
    upper_red = np.array([35,255,255])
    mask = cv2.inRange(hsv_img, lower_red, upper_red)
    mask1 = cv2.inRange(hsv_img, lower_red, upper_red)
    #lower_red = np.array([155,90,70])
    #upper_red = np.array([179,255,255])
    lower_red = np.array([145,30,40])
    upper_red = np.array([179,255,255])
    mask2 = cv2.inRange(hsv_img, lower_red, upper_red)
    mask = np.bitwise_or(mask1, mask2)
    org_2_img = mask.copy()

    '''
    -------------
    dilate the masked image so that it's easier to draw bounding rect
    -------------
    '''
    #dilation
    digit_height = int(dynamic_height[len(dynamic_height) // 2] * (0.58))
    kernel = np.ones((int(digit_height / 10), 1), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations = 1)
    #kernel = np.ones((5, 1), np.uint8)
    #mask = cv2.dilate(mask, kernel, iterations = 1)

    '''
    -------------
    - Save undilated image since it's more 'recognizable'
    - Detect rects for red_number_sequence
    -------------
    '''
    mask = mask_process(mask, points)
    mask_w_o_dilation = mask_process(org_2_img, points)

    im2, sct_cnts, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects = [cv2.boundingRect(cnt) for cnt in sct_cnts]
    rects = [rect for rect in rects if rect[2] < rect[3]]
    if len(rects) == 0:
        return 0

    rects = sorted(rects, key=lambda x: x[0])
    y = sorted(rects, key=lambda x: x[1])
    y = y[len(y)/2][1]
    rects = [rect for rect in rects if rect[1] >= y * 0.8 and rect[1] <= y * 1.23]

    res = cv2.bitwise_and(gray, gray, mask=mask)

    '''
    -------------
    Dilate the original image a little bit to improve accuracy
    -------------
    '''
    kernel = np.ones((2, 1), np.uint8)
    mask_w_o_dilation = cv2.dilate(mask, kernel, iterations = 1)
    '''
    -------------
    Pour numbers into number recognition program (adjusted to decrease False Positive rate which in turn increase False negative rate)
    -------------
    '''
    secret_ids = []
    for rect in rects:
        if mask[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]].mean() > 240:
            secret_ids.append(1)
        else:
            secret_ids.append(num_recog.digit_recognition(pad_diggit(mask_w_o_dilation[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]])))

    '''
    -------------
    If the output sequence is uncertain, use outputs from neural network instead
    -------------
    '''
    if -1 in secret_ids:
        for rect in rects:
            secrets = np.array([pad_diggit(org_2_img[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]]) for rect in rects], dtype='float32')
            secrets = secrets[:,None,...].astype('float32') / 255
            net.blobs['data'].reshape(secrets.shape[0], 1, 28, 28)
            net.blobs['data'].data[...] = secrets
            out = net.forward()
            secret_ids = out['prob'].argmax(axis = 1)

    if len(secret_ids) == 5:
        red_output_sequence = [i for i in secret_ids]
        update_record(red_number_sequence = red_output_sequence)
        if _DEBUG:
            print "Red: " + str(red_output_sequence)


    return 1

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    while True:
        ret, img = cap.read()
        img = process(img)
        #cv2.imshow('go', img)
        #vout.write(img)
        #vout.write(img)
        if time.time() - start_time >= 2:
            break

    #Send desired position
    ret = calculate_position_2_hit(prv_red_seq, prv_hit_round)
    print ret
    #Cleanup
    cap.release()
