import cv2
import numpy as np
from IPython import embed
import caffe

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
fourcc = cv2.VideoWriter_fourcc(*'MP4V')
vout = cv2.VideoWriter('output.mp4', fourcc, 20.0, (1280,720))

while True:
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret3,thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
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
    '''
    rects = [cv2.boundingRect(cnt) for cnt in contours]
    new_rects = []
    for rect in rects:
        scale = rect[2] * 1.0 / rect[3];
        if scale >= 2.3 or scale <= 1.6 or rect[2] <= 40 or rect[2] >= 250:
            continue
        new_rects.append(rect)
    if len(new_rects) < 9:
        continue
    new_rects = np.array(new_rects)
    height = np.median(new_rects[:,3])
    rects = [rect for rect in new_rects if rect[3] >= .95 * height]
    for rect in rects:
        cv2.rectangle(img, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (0, 255, 0), 3)
        gray = cv2.GaussianBlur(gray, (5,5), 0)
    '''
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


    for i in range(len(contours)):
        cv2.putText(img, str(dig_ids[i]),
                    (int(contours[i][0,0]), int(contours[i][0,1]-20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                   (255,0,0),
                   2,cv2.LINE_AA)

    cv2.imshow('go', img)
    vout.write(img)
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

vout.release()
cam.release()
cv2.destroyAllWindows()
