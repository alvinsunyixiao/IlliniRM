from camera import VideoCamera
import socket
import numpy as np
from tqdm import tqdm
import cv2
import time

vc = VideoCamera("nvcamerasrc ! video/x-raw(memory:NVMM), width=(int)1280, height=(int)720,format=(string)I420,framerate=(fraction)120/1 ! nvvidconv flip-method=0 ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw,format=(string)BGR ! appsink", True)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = ('192.168.0.111',2355)

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
        time.sleep(0.007)


