# coding: utf-8
# Load Neccessary Libraries
import caffe
import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import buff_benchmark_comm

# Load caffe model
caffe.set_mode_cpu()

net = caffe.Net('./model/lenet.prototxt',
                './model/mnist_iter_200000.caffemodel',
               caffe.TEST)


# Swap 2 objects
def swap(a,b):
    return b,a

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

def sort_points(rect):
    x_sort = np.array(sorted(rect, key=lambda x: x[1]))
    if x_sort[0,0] > x_sort[1,0]:
        x_sort[0,0], x_sort[1,0] = swap(x_sort[0,0], x_sort[1,0])
    if x_sort[2,0] > x_sort[3,0]:
        x_sort[2,0], x_sort[3,0] = swap(x_sort[2,0], x_sort[3,0])
    return x_sort

def find_contour_bound(cont):
    left_bound = min(cont, key = lambda x: x[0])[0]
    right_bound = max(cont, key = lambda x: x[0])[0]
    lower_bound = min(cont, key = lambda x: x[1])[1]
    upper_bound = max(cont, key = lambda x: x[1])[1]
    return (left_bound, right_bound, lower_bound, upper_bound)

# Load image and compute its threshold binary map

def filterRects(rect):
    left_bound, right_bound, lower_bound, upper_bound = find_contour_bound(rect)
    x = right_bound - left_bound
    y = float(upper_bound) - lower_bound
    if y / x >= 0.3 and y / x <= 0.55:
        return True
    return False

def process(img, client1 = None, pos = -1):
    #img = cv2.resize(img, (800,600))
    img_cp = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7,7), 0)
    ret3,thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    # Find all contours
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Filter out contours that are either too big or too small
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= 100*50 and cv2.contourArea(cnt) <= 240*120]
    # Find contour approximation and enforce a 4-sided convex shape
    '''
    tmp = []
    for cnt in contours:
        epsilon = 0.05*cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt,epsilon,True)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            tmp.append(approx)

    if len(tmp) == 0:
        return img

    contours = np.array(tmp)[:,:,0,:]
    cv2.drawContours(img, contours, -1, (0,255,0), 3)
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


    BOX_LEN = 32                # bounding box length for digits
    offset = (BOX_LEN - 28) / 2 # calculated padding length
    # Destination Points
    dstpts = np.array([[0,0],[BOX_LEN,0],[0,BOX_LEN],[BOX_LEN,BOX_LEN]], dtype='float32')

    bboxs = []
    points = []

    for cnt in contours:
        # Sort points with respect to relative location
        pts1 = sort_points(cnt).astype('float32')
        points.append(pts1)
        # Geometric transformation that project the 4-sided shape onto a 32x32 grid
        M = cv2.getPerspectiveTransform(pts1,dstpts)
        new_img = cv2.warpPerspective(gray,M,(BOX_LEN,BOX_LEN))
        new_img = 255 - new_img[offset:-offset, offset:-offset]
        bboxs.append(new_img)

    bboxs = np.array(bboxs)[:, None,...]

    net.blobs['data'].reshape(bboxs.shape[0], 1, 28, 28)
    net.blobs['data'].data[...] = bboxs.astype('float32') / 255
    out = net.forward()
    dig_ids = out['prob'].argmax(axis = 1)

    for i in range(len(points)):
        cv2.putText(img, str(dig_ids[i]),
                    (int(points[i][0,0]), int(points[i][0,1]-20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                   (0,255,255),
                   2,cv2.LINE_AA)

    if len(contours) == 9:
        output_sequence = rank(dig_ids, contours)
        client1.update(input_sequence = output_sequence)
        print "White: " + str(output_sequence)

    org_img = img_cp.copy()
    hsv_img = cv2.cvtColor(org_img, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0,90,70])
    upper_red = np.array([15,255,255])
    mask = cv2.inRange(hsv_img, lower_red, upper_red)
    mask1 = cv2.inRange(hsv_img, lower_red, upper_red)
    lower_red = np.array([165,90,70])
    upper_red = np.array([179,255,255])
    mask2 = cv2.inRange(hsv_img, lower_red, upper_red)
    mask = np.bitwise_or(mask1, mask2)

    kernel1 = np.ones((9,9),np.uint8)
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
    mask = cv2.bitwise_and(mask, mask, mask=ftr)

    #dilation
    #kernel = np.ones((8, 10), np.uint8)
    #mask = cv2.dilate(mask, kernel, iterations = 1)

    im2, sct_cnts, hierarchy = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    rects = [cv2.boundingRect(cnt) for cnt in sct_cnts]
    rects = [rect for rect in rects if rect[2] < rect[3]]
    if len(rects) == 0:
        return img

    rects = sorted(rects, key=lambda x: x[0])
    y = sorted(rects, key=lambda x: x[1])
    y = y[len(y)/2][1]
    rects = [rect for rect in rects if rect[1] >= y*0.9 and rect[1] <= y*1.1]


    if pos != -1 and pos < len(rects):
        cv2.rectangle(img, (rects[pos][0], rects[pos][1]),
                           (rects[pos][0]+rects[pos][2], rects[pos][1]+rects[pos][3]),
                           (0,255,0),3)

    res = cv2.bitwise_and(gray, gray, mask=mask)

    secrets = np.array([pad_diggit(mask[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]]) for rect in rects], dtype='float32')
    secrets = secrets[:,None,...].astype('float32') / 255
    net.blobs['data'].reshape(secrets.shape[0], 1, 28, 28)
    net.blobs['data'].data[...] = secrets
    out = net.forward()
    secret_ids = out['prob'].argmax(axis = 1)
    #print dig_ids

    if pos != -1 and pos < len(secret_ids):
        num = secret_ids[pos]
        idx = np.argwhere(dig_ids == num).flatten()
        if idx.shape[0] == 0:
            return img
        idx = idx[0]
        cv2.drawContours(img, contours, idx, (0,0,255), 3)

    if len(secret_ids) == 5:
        red_output_sequence = [i for i in secret_ids]
        client1.update(red_number_sequence = red_output_sequence)
        print "Red: " + str(red_output_sequence)


    return img


cap = cv2.VideoCapture(0)

#fourcc = cv2.VideoWriter_fourcc(*'MP4V')
#vout = cv2.VideoWriter('output.mp4', fourcc, 20.0, (1280,720))
client = buff_benchmark_comm.client()

while True:
    for i in range(5):
        for j in range(4):
            ret, img = cap.read()
            img = process(img, client1 = client, pos =  i)
            cv2.imshow('go', img)
            #vout.write(img)
            #vout.write(img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        for j in range(4):
            ret, img = cap.read()
            img = process(img, client1 = client)
            cv2.imshow('go', img)
            #vout.write(img)
            #vout.write(img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break



cap.release()
