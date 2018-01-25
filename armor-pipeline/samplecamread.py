#
#   Eric Liang 1/24
#   Sample Camera Reader for USB cameras
#   This is really important. When you are using USB cameras, the highest frame rate might not be achieved at the lowest possible resolution (say 480p).
#   Instead, test different values of width/height to get the highest frame rate.
#   And if you comment out MJPG, the speed will be dramatically reduced.
#

import cv2  #OpenCV
import time #Time module to measure fps

width = 1280    #Frame width
height = 720    #Frame size


if __name__ == '__main__':
    cap = cv2.VideoCapture(0)   #0/1/2 depending on how many cameras you have, change when it's not the one you want to use
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))    #Change to MJPG for faster response
    #cap.set(cv2.CAP_PROP_EXPOSURE, 0)  #This sets the exposure value, when this value is high, frame rate is reduced
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)    #width
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)  #height


    while True:
        t = time.time() #Time measure
        ret,img = cap.read()    #Read
        dt = time.time() - t
        cv2.putText(img,'fps: %.1f fps' % (1/dt),(30,30),0,1,(0,255,0))
        cv2.imshow('sample',img)    #Show
        cv2.waitKey(1)
