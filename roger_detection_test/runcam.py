import cv2
import numpy as np
from IPython import embed
import caffe
from copy import deepcopy
import math
import opencv_contour_hierarchy_tree as treeprocessor

caffe.set_mode_cpu()

net = caffe.Net('./model/lenet.prototxt',
                './model/lenet_iter_50000.caffemodel',
                caffe.TEST)

def swap(a,b):
    return b,a

def sort_points(rect):
    x_sort = np.array(sorted(rect, key=lambda x: x[1]))
    if x_sort[0,0] > x_sort[1,0]:
        x_sort[0,0], x_sort[1,0] = swap(x_sort[0,0], x_sort[1,0])
    if x_sort[2,0] > x_sort[3,0]:
        x_sort[2,0], x_sort[3,0] = swap(x_sort[2,0], x_sort[3,0])
    return x_sort

cam = cv2.VideoCapture(0)
#fourcc = cv2.VideoWriter_fourcc(*'MP4V')
#vout = cv2.VideoWriter('output.mp4', fourcc, 20.0, (1280,720))

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

while True:
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #ret3, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    otsu_threshold, dump = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    offsetted_threshold = otsu_threshold + (255 - otsu_threshold) * 0.08
    ret3, thresh = cv2.threshold(gray, offsetted_threshold, 255, cv2.THRESH_BINARY)
    im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    extracted_hierarchy = hierarchy[0]
    holder_frame = treeprocessor.contour_with_n_contour_inside(extracted_hierarchy, 9)
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= 120*60 and cv2.contourArea(cnt) <= 300*150]
    tmp = []
    for cnt in contours:
        epsilon = 0.05*cv2.arcLength(cnt, True)
        new_cnt = cv2.approxPolyDP(cnt,epsilon,True)
        if len(new_cnt) == 4 and cv2.isContourConvex(new_cnt):
            tmp.append(new_cnt)
    if len(tmp) == 0:
        continue
    contours = np.array(tmp)[:,:,0,:]
    BOX_LEN = 32
    offset = (BOX_LEN - 28) / 2

    dstpts = np.array([[0,0],[BOX_LEN,0],[0,BOX_LEN],[BOX_LEN,BOX_LEN]], dtype='float32')
    bboxs = []
    tmp = []

    for cnt in contours:
        pts1 = sort_points(cnt).astype('float32')
        tmp.append(pts1)
        M = cv2.getPerspectiveTransform(pts1,dstpts)
        new_img = cv2.warpPerspective(gray,M,(BOX_LEN,BOX_LEN))
        new_img = new_img[offset:-offset, offset:-offset]
        bboxs.append(new_img)

    cv2.drawContours(img, contours, -1, (0,255,0), 3)

    contours = tmp

    bboxs = np.array(bboxs)[:, None,...]
    net.blobs['data'].reshape(bboxs.shape[0], 1, 28, 28)
    net.blobs['data'].data[...] = bboxs
    out = net.forward()
    dig_ids = out['prob'].argmax(axis = 1)
    print(dig_ids)


    for i in range(len(contours)):
        cv2.putText(img, str(dig_ids[i]),
                    (int(contours[i][0,0]), int(contours[i][0,1]-20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                   (0,255,255),
                   2,cv2.LINE_AA)

    if len(tmp) == 9:
        print("Ranked: " + str(rank(dig_ids, contours)))
    cv2.imshow('go', img)
    #vout.write(img)
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

#vout.release()
cam.release()
cv2.destroyAllWindows()
