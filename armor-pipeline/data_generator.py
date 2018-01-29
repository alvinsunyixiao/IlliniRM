import cv2
import numpy as np
import scipy as scp
import math

_WIDTH = 100
_HEIGHT = 100
counter = 0

def drawRect(img, rect):
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    cv2.drawContours(img,[box],0,(0,255,0),2)

def swap(a,b):
    return b,a

def minmax(a, b):
    return (a, b) if a < b else (b, a)

def sort_points(rect):
    x_sort = np.array(sorted(rect, key=lambda x: x[1]))
    if x_sort[0,0] > x_sort[1,0]:
        x_sort[0,0], x_sort[1,0] = swap(x_sort[0,0], x_sort[1,0])
    if x_sort[2,0] > x_sort[3,0]:
        x_sort[2,0], x_sort[3,0] = swap(x_sort[2,0], x_sort[3,0])
    return x_sort

class Armor:
    RED_THRESH = 50
    BLUE_THRESH = 90
    GRAY_THRESH = 200 # Official Version Set to 200

    LIGHT_MIN_ASPECT_RATIO = 2
    LIGHT_MAX_ANGLE = 30.0
    LIGHT_MIN_AREA = 4.0
    LIGHT_MAX_ANGLE_DIFF = 30.0

    ARMOR_MAX_ANGLE = 20.0
    ARMOR_MIN_AREA = 40.0
    ARMOR_MAX_ASPECT_RATIO = 3.0

    def __init__(self):
        pass

    def preprocess(self, img):
        self._img = img
        self._gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def color_thresh(self, color):
        bgr = cv2.split(self._img)
        result = None
        if (color == 'red'):
            result = bgr[2] - bgr[1]
            thresh = self.RED_THRESH
        elif (color == 'blue'):
            result = bgr[0] - bgr[2]
            thresh = self.BLUE_THRESH
        if result is None:
            return None
        self._color_highlight = result
        ret, result = cv2.threshold(result, thresh, 255, cv2.THRESH_BINARY)
        if not ret:
            return None
        kernal = np.ones((3,3), dtype=np.uint8)
        result = cv2.dilate(result, kernal, iterations=1)
        result &= self._gray_bin
        self._light_bin = result
        return result

    def gray_thresh(self):
        ret, result = cv2.threshold(self._gray_img, self.GRAY_THRESH, 255, cv2.THRESH_BINARY)
        if not ret:
            return None
        else:
            self._gray_bin = result
            return result

    def light_detect(self, color):
        self.gray_thresh()
        self.color_thresh(color)

        cnt_method = cv2.CHAIN_APPROX_NONE
        cnt_mode = cv2.RETR_EXTERNAL

        im1, light_cnt, hier1 = cv2.findContours(self._light_bin, cnt_mode, cnt_method)
        im2, gray_cnt, hier2 = cv2.findContours(self._gray_bin, cnt_mode, cnt_method)

        proc_flag = np.zeros(len(gray_cnt), dtype=bool)
        light_rects = []

        for i in range(len(light_cnt)):
            for j in range(len(gray_cnt)):
                if not proc_flag[j]:
                    if cv2.pointPolygonTest(gray_cnt[j], tuple(light_cnt[i][0][0]), True) >= 0.0:
                        light_rects.append(cv2.minAreaRect(gray_cnt[j]))
                        proc_flag[j] = True
                        break
        self._lights = light_rects
        return light_rects

    def light_filter(self):
        f_rects = []
        for rect in self._lights:
            r1 = max(rect[1][0], 1.0)
            r2 = max(rect[1][1], 1.0)
            ang = rect[2]
            asp_ratio = 1.0* max(r1, r2) / min(r1, r2)
            new_ang = abs(abs(ang)-90) if max(r1, r2) == r1 else abs(ang)
            if (asp_ratio > self.LIGHT_MIN_ASPECT_RATIO and
               new_ang < self.LIGHT_MAX_ANGLE and r1*r2 >= self.LIGHT_MIN_AREA):
                if max(r1, r2) == r2:
                    f_rects.append(rect)
                else:
                    f_rects.append((rect[0], (r2, r1), new_ang))
        self._lights = f_rects
        return f_rects

    def armor_detect(self):
        a_rects = []
        for i in range(len(self._lights)-1):
            for j in range(i+1, len(self._lights)):
                light1 = self._lights[i]
                light2 = self._lights[j]
                edge1 = minmax(light1[1][0], light1[1][1])
                edge2 = minmax(light2[1][0], light2[1][0])
                light_dis = math.sqrt((light1[0][0] - light2[0][0])**2 + \
                                      (light1[0][1] - light2[0][1])**2)
                bbox_ang = math.atan((light1[0][1] - light2[0][1]) / \
                                     (light1[0][0] - light2[0][0] + 1e-8)) * 180 / math.pi
                bbox_x = (light1[0][0] + light2[0][0]) / 2
                bbox_y = (light1[0][1] + light2[0][1]) / 2
                bbox_h = max(edge1[1], edge2[1]) * 2
                bbox_w = light_dis * 1.2
                bbox = ((bbox_x, bbox_y), (bbox_w, bbox_h), bbox_ang)
                if abs(light1[2] - light2[2]) < self.LIGHT_MAX_ANGLE_DIFF and \
                abs(bbox_ang) < self.ARMOR_MAX_ANGLE and \
                bbox_w / bbox_h < self.ARMOR_MAX_ASPECT_RATIO and \
                bbox_h*bbox_w > self.ARMOR_MIN_AREA:
                    a_rects.append(bbox)
        self._armor_rects = a_rects
        return a_rects

    def _armor_frameprocess(self, _img, color):
        self.preprocess(_img)
        self.light_detect(color)
        self.light_filter()
        return self.armor_detect()

def main(video_name, color):
    global counter
    frame_counter = 0
    cap = cv2.VideoCapture(video_name)
    armor = Armor()
    while True:
        ret, img = cap.read()
        frame_counter += 1
        if not ret: break
        if frame_counter % 10 != 0: continue
        print "Now processing frame " + str(frame_counter) + " of " + video_name
        armors = armor._armor_frameprocess(img, color)
        for armor_rect in armors:
            box = cv2.boxPoints(armor_rect)
            pts1 = sort_points(box).astype("float32")
            desired_img_pts = np.array([[0, 0], [_HEIGHT, 0], [0, _WIDTH], [_HEIGHT, _WIDTH]], dtype = "float32")
            M = cv2.getPerspectiveTransform(pts1, desired_img_pts)
            new_img = cv2.warpPerspective(img, M, (_HEIGHT, _WIDTH))
            cv2.imwrite("armor_board/" + str(counter) + ".jpg", new_img)
            counter += 1

if __name__ == '__main__':
    main("red_front.mp4", "red")
