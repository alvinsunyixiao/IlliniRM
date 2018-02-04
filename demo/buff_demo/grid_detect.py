# coding: utf-8
# Load Neccessary Libraries
import caffe
import cv2
import numpy as np
import buff_autoshoot_config as config
#import matplotlib.pyplot as plt
#from scipy import stats
#import buff_benchmark_comm
import new_num_recog
import time
#from pprint import pprint

_DEBUG = False
BATCHSIZE = 9

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
    kernel1 = np.ones((4, 5),np.uint8)
    kernel2 = np.ones((3, 3),np.uint8)
    kernel3 = np.ones((2, 7),np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel3)

    y_min = min(points,key=lambda cnt: cnt[0,1])[0,1]
    y_min = int(y_min)
    x_min1 = min(points, key=lambda cnt: cnt[1,0])[1,0]
    x_min1 = int(x_min1)
    x_min2 = max(points, key=lambda cnt: cnt[0,0])[0,0]
    x_min2 = int(x_min2)
    ftr = np.ones(mask.shape[0:2],np.uint8)
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
    #print y / x
    if y / x >= 0.3 and y / x <= 0.6:
        return True
    return False

def process(img, net, client1 = None, pos = -1):
    #timer = {}
    #st = time.time()

    #img = cv2.resize(img, (640, 360))
    img_cp = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #TODO: mask peripheral part of the image to reduce glare influence
    gray = cv2.GaussianBlur(gray, (config.gaussian_factor, config.gaussian_factor), 0)
    ret3,thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    kernel = np.ones((config.cells_dilate_height, config.cells_dilate_width),np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    #timer['whole_img_threshold'] = time.time() - st
    #st = time.time()

    # Find all contours
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Filter out contours that are either too big or too small
    width, height = get_size(img)
    img_width_range = (config.width_lower_threshold * width, config.width_upper_threshold * width)
    img_height_range = (config.height_lower_threshold * height, config.height_upper_threshold * height)
    #contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= 100*40 and cv2.contourArea(cnt) <= 300*150]
    if _DEBUG:
        #print "len of contours before filtering: %d" % len(contours)
        pass
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= img_width_range[0] * img_height_range[0] and cv2.contourArea(cnt) <= img_width_range[1] * img_height_range[1] and filterRects(cnt, pure_cont = True)]
    if _DEBUG:
        pass
        #print "len of contours after filtering: %d" % len(contours)
    # Find contour approximation and enforce a 4-sided convex shape
    if _DEBUG:
        for cnt in contours:
            print cv2.contourArea(cnt)
    tmp = []
    for cnt in contours:
        epsilon = 0.05 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt,epsilon,True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            tmp.append(approx)

    if len(tmp) == 0:
        print "Point A"
        return -1, -1

    #timer['contour_approx'] = time.time() - st
    '''
    st = time.time()


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

    timer['manual_fix'] = time.time() - st
    '''
    contours = np.array(tmp)[:,:,0,:]
    #st = time.time()

    #cv2.drawContours(img, contours, -1, (0,255,0), 3)
    '''
    tmp = []
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        if filterRects(box):
            cv2.drawContours(img, [box], 0, (0, 255, 0), 3)
            tmp.append(box)

    if len(tmp) == 0:
        return img

    contours = tmp
    cv2.drawContours(img, contours, -1, (0, 255, 0), 3)
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

    while len(bboxs) < 9:
        bboxs.append(np.zeros((28, 28), np.uint8)) #fill in useless data

    while len(bboxs) > 9:
        del(bboxs[-1])

    bboxs = np.array(bboxs)[:, None,...]

    #timer['crop_digits'] = time.time() - st
    #st = time.time()

    net.blobs['data'].data[...] = bboxs.astype('float32') / 255
    out = net.forward()
    dig_ids = out['prob'].argmax(axis = 1)
    #timer['mnist_predict'] = time.time() - st

    '''
    for i in range(len(points)):
        cv2.putText(img, str(dig_ids[i]),
                    (int(points[i][0,0]), int(points[i][0,1]-20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                   (0,255,255),
                   2,cv2.LINE_AA)
    '''
    dig_ids = dig_ids[:len(contours)]
    if len(contours) != 9:
        return -1, -1

    if len(dig_ids) == 9: #TODO: data are potentially usable after rewriting rank function
        output_sequence = rank(dig_ids, contours)
    else:
        output_sequence = -1
    #client1.update(input_sequence = output_sequence)
    if _DEBUG:
        print "White: " + str(output_sequence)

    #st = time.time()
    org_img = img_cp.copy()
    bgr = cv2.split(org_img).astype(int)
    red = bgr[2] - bgr[1]
    ret, red_mask = cv2.threshold(red, 90, 255, cv2.THRESH_BINARY)
    org_2_img = red_mask.copy()
    kernel = np.ones((3,3), dtype=np.uint8)
    mask = cv2.morphologyEx(red_mask, cv2.MORPH_DILATE, kernel).astype('uint8')
    '''
    hsv_img = cv2.cvtColor(org_img, cv2.COLOR_BGR2HSV)
    lower_red = np.array(config.first_lower_red_range)
    upper_red = np.array(config.first_upper_red_range)
    mask = cv2.inRange(hsv_img, lower_red, upper_red)
    mask1 = cv2.inRange(hsv_img, lower_red, upper_red)
    lower_red = np.array(config.second_lower_red_range)
    upper_red = np.array(config.second_upper_red_range)
    mask2 = cv2.inRange(hsv_img, lower_red, upper_red)
    mask = np.bitwise_or(mask1, mask2)
    org_2_img = mask.copy()

    #dilation
    digit_height = int(dynamic_height[len(dynamic_height) // 2] * config.red_digit_height_scaling_factor)
    kernel = np.ones((int(digit_height / 20), 1), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations = 2)
    #kernel = np.ones((5, 1), np.uint8)
    #mask = cv2.dilate(mask, kernel, iterations = 1)


    '''
    mask = mask_process(mask, points)
    mask_w_o_dilation = mask_process(org_2_img, points)

    #timer['mask_processing'] = time.time() - st
    #st = time.time()

    im2, sct_cnts, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.imwrite("debug.jpg", mask)
    rects = [cv2.boundingRect(cnt) for cnt in sct_cnts]
    rects = [rect for rect in rects if rect[2] < rect[3] + 5]
    if len(rects) == 0:
        print "Point B"
        return output_sequence, -1

    rects = sorted(rects, key=lambda x: x[0])
    y = sorted(rects, key=lambda x: x[1])
    y = y[len(y)/2][1]
    rects = [rect for rect in rects if rect[1] >= y * 0.7 and rect[1] <= y * 2.1]
    #print "--------"
    #print len(rects)

    #timer['bound_red_number'] = time.time() - st
    #st = time.time()

    '''
    if pos != -1 and pos < len(rects):
        cv2.rectangle(img, (rects[pos][0], rects[pos][1]),
                           (rects[pos][0]+rects[pos][2], rects[pos][1]+rects[pos][3]),
                           (0,255,0),3)
                           '''

    res = cv2.bitwise_and(gray, gray, mask=mask)
    '''
    secrets = np.array([pad_diggit(org_2_img[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]]) for rect in rects], dtype='float32')
    secrets = secrets[:,None,...].astype('float32') / 255
    net.blobs['data'].reshape(secrets.shape[0], 1, 28, 28)
    net.blobs['data'].data[...] = secrets
    out = net.forward()
    secret_ids = out['prob'].argmax(axis = 1)
    #print dig_ids
    '''
    kernel = np.ones((2, 1), np.uint8)
    mask_w_o_dilation = cv2.dilate(mask, kernel, iterations = 1)
    secret_ids = []
    for rect in rects:
        if mask[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]].mean() > 240:
            secret_ids.append(1)
        else:
            secret_ids.append(new_num_recog.digit_recognition(pad_diggit(mask_w_o_dilation[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]]))) #TODO: mask or mask_w_o_dilation?

    #print secret_ids
    secret_ids = [-1, -1]

    if -1 in secret_ids:
        secrets = np.array([pad_diggit(org_2_img[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]]) for rect in rects], dtype='float32')
        secrets = secrets[:,None,...].astype('float32') / 255
        pad_size = BATCHSIZE - secrets.shape[0]
        zeros = np.zeros((pad_size,1,28,28),dtype='float32')
        net.blobs['data'].data[...] = np.concatenate([secrets,zeros], axis=0)
        out = net.forward()
        secret_ids = out['prob'].argmax(axis = 1)
        secret_ids = secret_ids[:len(rects)]
    else:
        print "opencv proudnly present the answer!"

    #timer['secret_recognition'] = time.time() - st

    '''
    for i in range(len(rects)):
        cv2.putText(img, str(secret_ids[i]),
                    (int(rects[i][0]), int(rects[i][1] - 15)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                   (0,255,255),
                   2,cv2.LINE_AA)
    '''
    '''
    if pos != -1 and pos < len(secret_ids):
        num = secret_ids[pos]
        idx = np.argwhere(dig_ids == num).flatten()
        if idx.shape[0] == 0:
            return img
        idx = idx[0]
        cv2.drawContours(img, contours, idx, (0,0,255), 3)
    '''

    '''
    if len(secret_ids) != 5:
        return -1, -1
    if len(secret_ids) == 5:
        #client1.update(red_number_sequence = red_output_sequence)
        if _DEBUG:
            print "Red: " + str(red_output_sequence)
    '''

    red_output_sequence = [i for i in secret_ids]

    #print "End"
    return output_sequence, red_output_sequence

#cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture("nvcamerasrc ! video/x-raw(memory:NVMM), width=(int)640, height=(int)360,format=(string)I420, framerate=(fraction)60/1 ! nvvidconv flip-method=0 ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink")

#fourcc = cv2.VideoWriter_fourcc(*'MP4V')
#vout = cv2.VideoWriter('output.mp4', fourcc, 20.0, (1280,720))
#client = buff_benchmark_comm.client()

'''
while True:
    for i in range(5):
        for j in range(4):
            ret, img = cap.read()
            img, timer = process(img, client1 = client, pos =  i)
            if _DEBUG:
                bnk = max(timer.items(), key=lambda x:x[1])
                print('bottleneck: ', bnk[0], ': ', bnk[1])
                pprint(timer)
            cv2.imshow('go', img)
            #vout.write(img)
            #vout.write(img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        for j in range(4):
            ret, img = cap.read()
            img, timer = process(img, client1 = client)
            cv2.imshow('go', img)
            #vout.write(img)
            #vout.write(img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
'''
