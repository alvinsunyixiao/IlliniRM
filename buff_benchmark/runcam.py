import cv2
import numpy as np
from IPython import embed

cam = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'MP4V')
vout = cv2.VideoWriter('output.mp4', fourcc, 20.0, (1280,720))

while True:
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret3,thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
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
    cv2.imshow('go', img)
    vout.write(img)
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

vout.release()
cam.release()
cv2.destroyAllWindows()
