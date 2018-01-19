# -*- coding: utf-8 -*-
#Robomaster Color Tracking Code V0.1 By Weihang(Eric) Liang
#
#   Contributors:
#       V0.1: Weihang(Eric) Liang
#
#NOTE!!! This code is highly incomplete. Major updates incoming.

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


##  Resize factor and Gaussian factor are the main two factors that affect the performance of this code
##  Range resizefactor 0.1 - 1.0 (0.5)
##  Range Gaussianfactor 3,5,7,9,11 (5)
##  Higher = Better quality in recognizing targets Lower = Faster

resizefactor = 0.5  #Resize the image to this factor

Gaussianfactor = 3  #Blur factor

#tracking variables

trackedtargets = []

#tracking variables end

def resize (frame, factor): #Resizes the frame by factor
    height, width = frame.shape[:2]
    if factor == 1:
        return frame
    elif factor < 1:
        size = (int(width * factor), int(height * factor))
        return cv2.resize(frame, size, interpolation=cv2.INTER_AREA)
    else:
        size = (int(width * factor), int(height * factor))
        return cv2.resize(frame, size, interpolation=cv2.INTER_CUBIC)

def maskHSV (hsvframe, lowerBound, upperBound, Gaussianfactor): #Masks the HSV frame using color bounds
    if lowerBound[0] > upperBound[0]:
        midBound1 = np.array([179,upperBound[1],upperBound[2]])
        midBound2 = np.array([0,lowerBound[1],lowerBound[2]])
        mask = cv2.inRange(hsvframe, lowerBound, midBound1)
        mask += cv2.inRange(hsvframe, midBound2, upperBound)
    else:
        mask = cv2.inRange(hsvframe, lowerBound, upperBound)
    mask = cv2.GaussianBlur(mask, (Gaussianfactor,Gaussianfactor), 0)
    return mask


def findRects (conts):  #Find the minAreaRects according to the contour
    rects = []
    for cont in conts:
        rect = cv2.minAreaRect(cont)
        rects.append(rect)
    return rects


def filterRects (rects):    #Filter the rects according to the characteristics of armor
    newrects = []
    for rect in rects:
        point, size, ang = rect
        h, w = size
        if (h / w > 1.5 and (abs(ang) > 60)) or ((w/h > 1.5) and (abs(ang)<30)):
            newrects.append(rect)
    return newrects

def resizeRects (rects, factor):    #Resize the rects back to normal size
    if factor == 1:
        return rects
    newrects = []
    for rect in rects:
        point, size, ang = rect
        h, w = size
        x, y = point
        h /= factor
        w /= factor
        x /= factor
        y /= factor
        rect = ((x, y), (h, w), ang)
        newrects.append(rect)
    return newrects

def drawRects (frame, rects, color):    #Draw the rects on the frame
    for rect in rects:
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(frame, [box], 0, color, 2)

def recttransform (size, ang):  #make all the rects in desired format
    newang = ang
    h,w = size
    if ang < -60:
        newang = -90 - ang
        return w,h,newang
    elif ang > 60:
        newang = 90 - ang
        return w,h,newang
    return h,w,ang

def histroi (rect, hsv, mask):
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    boundrect = cv2.boundingRect(box)
    x0,y0,w,h = boundrect
    hsv_roi = hsv[y0:y0+h, x0:x0+w]
    mask_roi = mask[y0:y0+h, x0:x0+w]
    hist = cv2.calcHist([hsv_roi], [0], mask_roi, [16], [0, 180])
    #cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
    hist = hist.reshape(-1)
    return hist

def histroi2 (rect, hsv, mask):
    x0, y0, w, h = rect
    hsv_roi = hsv[y0+int(24*h/50):y0 + int(25*h/50), x0+int(24*w/50):x0 + int(25*w/50)]
    mask_roi = mask[y0+int(24*h/50):y0 + int(25*h/50), x0+int(24*w/50):x0 + int(25*w/50)]
    hist = cv2.calcHist([hsv_roi], [0], mask_roi, [16], [0, 180])
    cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
    hist = hist.reshape(-1)
    return hist

def inittrack(rects, hsv, mask):
    global trackedtargets
    trackedtargets = []
    lights = []
    hists = []
    track_windows = []
    for rect in rects:
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        boundrect = cv2.boundingRect(box)
        lights.append(boundrect)
        track_windows.append(boundrect)
        hist = histroi2(boundrect, hsv, mask)
        hists.append(hist)
        trackedtargets.append([boundrect,boundrect,hist])

def updatetracks(hsv):
    global trackedtargets
    term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 100, 1)
    for a in range(len(trackedtargets)):
        trackedtarget = trackedtargets[a]
        target, lasttrackwindow, hist = trackedtarget
        prob = cv2.calcBackProject([hsv], [0], hist, [0, 180], 1)
        track_box, track_window = cv2.CamShift(prob, lasttrackwindow, term_crit)
        trackedtargets[a] = [track_box, track_window, hist]

def drawtrackedtarget(frame, trackedtargets, color):
    for trackedtarget in trackedtargets:
        trackbox = trackedtarget[0]
        trackwindow = trackedtarget[1]
        x,y,w,h = trackwindow
        pts = cv2.boxPoints(trackbox)
        pts = np.int0(pts)
        cv2.polylines(frame, [pts], True, color, 2)
        # cv2.ellipse(frame, trackbox, (0, 0, 255), 2)
        #cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)


def findTargets (rects):    #Find the target armor using hard coded methods
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

            a1 = w1 * h1
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

            # score += 100
            # for blackcont in blackconts:
            #     if (cv2.pointPolygonTest(blackcont, (xmid, ymid), False)):
            #         score -= 100
            #         break

            if score < 5:
                targets.append((xmid, ymid))
                scores.append(score)

    sortedtargets = [target for _, target in sorted(zip(scores, targets))]
    return sortedtargets


if __name__ == '__main__':
    cap = cv2.VideoCapture('testvideo/炮台素材红车后面-ev-0.mp4')  #Open video file
    count = 0
    while (cap.isOpened()): #If there is video
        ret,frame = cap.read()  #Read the frame

        if not ret: #if there is no frame
            break   #end program

        #resizedframe = resize(frame, resizefactor)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)    #Convert RGB to HSV for value check



        if(len(trackedtargets) < 2 or count > 20):
            count = 0
            maskred = maskHSV(hsv, lowerredBound, upperorangeBound, Gaussianfactor)
            imred, redconts, hred = cv2.findContours(maskred.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)   #Finding contours of red points
            redrects = filterRects(findRects(redconts))

            inittrack(redrects,hsv,maskred)

            #redrects = resizeRects(redrects,resizefactor)

            drawRects(frame, redrects, (0, 255, 0))
            # redtargets = findTargets(redrects)
            # for a in range(min(1, int(len(redtargets)))):
            #     cv2.circle(frame, redtargets[a], 20, (0, 0, 255), -1)
        else:
            updatetracks(hsv)
            drawtrackedtarget(frame, trackedtargets, (0,255,0))
            count +=1

        cv2.imshow("video", frame)
        cv2.waitKey(1)

    cv2.destroyAllWindows()
    cap.release()

