import cv2
import numpy as np
from IPython import embed
import caffe
from copy import deepcopy
import math

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

def _in_the_course(x1, y1, x2, y2, px, py, error_allowed): #not used
    distance_from_course = abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1) / math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
    if distance_from_course <= error_allowed: return True
    return False

median = lambda a_array: sorted(a_array)[len(a_array) / 2]

cam = cv2.VideoCapture(0)
#fourcc = cv2.VideoWriter_fourcc(*'MP4V')
#vout = cv2.VideoWriter('output.mp4', fourcc, 20.0, (1280,720))

def cluster_row(unranked, lower_bound, upper_bound, max_correction = 30): #not used
    std_arr = unranked[0]
    std_y = std_arr[1]
    error_allowed = (float(upper_bound) - lower_bound) / 2
    temp = [i for i in unranked if (i[1] >= std_y - error_allowed and i[1] <= std_y + error_allowed)]
    if len(temp) == 3:
        for i in temp:
            unranked.remove(i)
        return temp
    elif len(temp) > 3:
        return cluster_row(unranked, lower_bound, error_allowed)
    else:
        return cluster_row(unranked, error_allowed, upper_bound)

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

'''
def rank(dig_ids, contours_array): #input contours array and correseponding dig_ids, output a sorted list of 9 digits
    unranked_list = []
    assert len(contours_array) == 9
    RANK_COURSE_ERROR = abs(contours_array[0][1, 1] - contours_array[0][2, 1])
    for n, con in enumerate(contours_array):
        x, y = int(con[1,0]), int(con[1,1])
        right_x, right_y = int(con[0,0]), int(con[0,1])
        unranked_list.append([x, y, dig_ids[n], right_x, right_y])
    #ranked_list = [[(0, 0, 0) for i in range(3)] for i in range(3)]
    ranked_list = []
    print contours_array
    print unranked_list

    #Calculate avg slope (upper right corner and upper left corner) and transform y
    avg_slope = median([((float(i[4]) - i[1]) / (i[3] - i[0])) for i in unranked_list])
    avg_rec_width = median([i[3] - i[0] for i in unranked_list])
    avg_rec_height = avg_rec_width * (2 / 3.0)
    for i in unranked_list:
        i[1] = i[1] - i[0] * avg_slope #transform y
    for i in range(3):
        print(unranked_list)
        ranked_list.append(cluster_row(unranked_list, lower_bound = 0, upper_bound = avg_rec_height * 2))
    ranked_list = sorted(ranked_list, key = lambda x: (x[0][1] + x[2][1]) / 2.0)
    return [i[2] for i in [j for j in ranked_list]]

    #alternative approach using distance between line and point
    while len(unranked_list) > 0:
        std_arr = unranked_list[0]
        this_row =[]
        for i in unranked_list:
            if _in_the_course(std_arr[0], std_arr[1], std_arr[3], std_arr[4], i[0], i[1], RANK_COURSE_ERROR):
                unranked_list.remove(i)
                this_row.append(i)
        this_row = sorted(this_row, key = lambda x: x[0])
        ranked_list.append(this_row)
    print ranked_list
    ranked_list = sorted(ranked_list, key = lambda x: (x[0][1])) # + x[2][1]) / 2)
    return [i[2] for i in [j for j in ranked_list]]

'''

while True:
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret3, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    #otsu_threshold, dump = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    #offsetted_threshold = otsu_threshold + (255 - otsu_threshold) * 0.08
    #ret3, thresh = cv2.threshold(gray, offsetted_threshold, 255, cv2.THRESH_BINARY)
    im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= 120*60 and cv2.contourArea(cnt) <= 300*150]
    tmp = []
    for cnt in contours:
        epsilon = 0.05*cv2.arcLength(cnt, True)
        new_cnt = cv2.approxPolyDP(cnt,epsilon,True)
        if len(new_cnt) == 4 and cv2.isContourConvex(new_cnt):
            #sorted_pts = sort_points(new_cnt)
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
