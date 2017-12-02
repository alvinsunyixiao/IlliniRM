# -*- coding: utf-8 -*-
#Robomaster Color Detection Code V0.1 By Weihang(Eric) Liang
#
#   Contributors:
#       V0.1: Weihang(Eric) Liang
#


import numpy as np  #numpy for doing calculations
import cv2  #Opencv 2


redH = [160,179]    #Red Hue Value Range
orangeH = [0,17]    #Orange Hue Value Range
blueH = [75,130]    #Blue Hue Value Range

S = [90,255]    #Saturation Factor (doesn't really matter)

V = [240,255]   #Value for light emitting devices

BlackV = [0,10] #Black value (darkness)

lowerredBound =  np.array([redH[0],S[0],V[0]])  #Setting up lower bounds for Red
upperredBound = np.array([redH[1],S[1],V[1]])   #Setting up higher bounds for Red

lowerorangeBound =  np.array([orangeH[0],S[0],V[0]])    #Setting up lower bounds for Orange (In effect Red)
upperorangeBound = np.array([orangeH[1],S[1],V[1]])     #Setting up higher bounds for Orange

lowerblueBound = np.array([blueH[0],S[0],V[0]])     #Setting up lower bounds for Blue
upperblueBound = np.array([blueH[1],S[1],V[1]])     #Setting up higher bounds for Blue

lowerblackBound = np.array([0,0,BlackV[0]])         #Setting up lower bounds for Black
upperblackBound = np.array([255,180,BlackV[1]])     #Setting up higher bounds for Black


def maskHSV (hsvframe, lowerBound, upperBound):
    if lowerBound[0] > upperBound[0]:
        midBound1 = np.array([179,upperBound[1],upperBound[2]])
        midBound2 = np.array([0,lowerBound[1],lowerBound[2]])
        mask = cv2.inRange(hsvframe, lowerBound, midBound1)
        mask += cv2.inRange(hsvframe, midBound2, upperBound)
    else:
        mask = cv2.inRange(hsvframe, lowerBound, upperBound)
    mask = cv2.GaussianBlur(mask, (7,7), 0)
    return mask


def findRects (conts):
    rects = []
    for cont in conts:
        rect = cv2.minAreaRect(cont)
        rects.append(rect)
    return rects


def filterRects (rects):
    newrects = []
    for rect in rects:
        point, size, ang = rect
        h, w = size
        if (h / w > 1.5 and (abs(ang) > 60)) or ((w/h > 1.5) and (abs(ang)<30)):
            newrects.append(rect)
    return newrects


def drawRects (frame, rects, color):
    for rect in rects:
        box = cv2.cv.BoxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(frame, [box], 0, color, 2)

def recttransform (size, ang):
    newang = ang
    h,w = size
    if ang < -60:
        newang = -90 - ang
        return w,h,newang
    elif ang > 60:
        newang = 90 - ang
        return w,h,newang
    return h,w,ang

def findTargets (rects, blackconts):
    targets = []
    scores = []
    for a in range(len(rects)):
        for b in range(a+1, len(rects)):
            score = 0
            rect1 = rects[a]
            rect2 = rects[b]

            point1, size1, ang1 = rect1
            point2, size2, ang2 = rect2

            x1, y1 = point1
            x2, y2 = point2

            h1, w1, ang1 = recttransform(size1, ang1)
            h2, w2, ang2 = recttransform(size2, ang2)


            xmid = int((x1 + x2) / 2)
            ymid = int((y1 + y2) / 2)

            a1 = w1 * w2
            a2 = w2 * h2

            wavg = (w1 + w2) / 2
            aavg = (a1 + a2) / 2
            adiff = abs(a1 - a2)

            dist = np.sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1))

            score += adiff / (a1 + a2)

            if x1 != x2:
                score += abs((y2 - y1) / (x2 - x1))
            else:
                score = 100

            score += 2 * abs(ang1 - ang2) / 180

            if (dist != 0):
                dwratio = dist / wavg
                score += 0.5 * abs(dwratio - 2) / 2
            else:
                score = 100

            score += 100
            for blackcont in blackconts:
                if (cv2.pointPolygonTest(blackcont, (xmid, ymid), False)):
                    score -= 100
                    break

            if score < 5:
                targets.append((xmid, ymid))
                scores.append(score)

    sortedtargets = [target for _, target in sorted(zip(scores, targets))]
    return sortedtargets


if __name__ == '__main__':
    cap = cv2.VideoCapture('testvideo/炮台素材蓝车后面-ev--3.mp4')  #Open video file

    while (cap.isOpened()): #If there is video
        ret,frame = cap.read()  #Read the frame

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)    #Convert RGB to HSV for value check

        maskred = maskHSV(hsv, lowerredBound, upperorangeBound)
        maskblue = maskHSV(hsv, lowerblueBound, upperblueBound)
        maskblack = maskHSV(hsv, lowerblackBound, upperblackBound)

        redconts, hred = cv2.findContours(maskred.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)   #Finding contours of red points
        blueconts, hblue = cv2.findContours(maskblue.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)    #Finding contours of blue points
        blackconts, hblack = cv2.findContours(maskblack.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  #Finding contours of black points

        redrects = filterRects(findRects(redconts))
        drawRects(frame, redrects, (0, 255, 0))
        redtargets = findTargets(redrects, blackconts)
        for a in range(min(1, int(len(redtargets)))):
            cv2.circle(frame, redtargets[a], 20, (0, 0, 255), -1)

        bluerects = filterRects(findRects(blueconts))
        drawRects(frame, bluerects, (0, 255, 255))
        bluetargets = findTargets(bluerects, blackconts)
        for a in range(min(1, int(len(bluetargets)))):
            cv2.circle(frame, bluetargets[a], 20, (230, 216, 173), -1)

        cv2.imshow("video", frame)
        cv2.waitKey(1)

    cv2.destroyAllWindows()
    cap.release()

