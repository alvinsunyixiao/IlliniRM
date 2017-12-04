import digit_displayer
from PIL import Image
import cv2
import os

directo = 'red_number/'

def main(desired_scale):
    for i in range(10):
        cur_digit = digit_displayer.digit(16, 24, width_scale = desired_scale)
        cur_digit.digit_update(i)
        cur_digit_img = cur_digit.generate()
        filename = directo + str(desired_scale) + '_' + str(i)
        black_bg = Image.new("RGB", (28, 28), "black")
        black_bg.paste(cur_digit_img, (7, 2, 23, 26))
        black_bg.save(filename + '.png')
        cur_img_numpy = cv2.imread(filename + '.png')
        #os.remove(filename + '.png')
        gray = cv2.cvtColor(cur_img_numpy, cv2.COLOR_BGR2GRAY)
        ret3, thresh = cv2.threshold(gray,60,255,cv2.THRESH_BINARY)
        print ret3
        cv2.imwrite(filename + '.jpg', thresh)

if __name__ == '__main__':
    for i in range(5, 40):
        main(i)
