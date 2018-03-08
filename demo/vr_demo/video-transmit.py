from camera import VideoCamera
import socket
import numpy as np
from tqdm import tqdm
import cv2

vc = VideoCamera(1,False)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = ('192.168.1.101',5657)

def itos(q):
    rs = ''
    for i in range(4):
        b = q & 0xFF
        rs = chr(b) + rs
        q = q >> 8
    return bytes(rs)

cnt = 0
while True:
    imdata = vc.get_frame()
    imlen = len(imdata)
    imlen_b = itos(imlen)
    s.sendto(imlen_b, dest)
    i = 0
    while i < imlen:
        s.sendto(imdata[i:min(i+5000,imlen)], dest)
        i += 5000

cap = cv2.VideoCapture(1)
ret, img = cap.read()
cap.release()

cv2.imshow('go', img)
cv2.waitKey(0)

