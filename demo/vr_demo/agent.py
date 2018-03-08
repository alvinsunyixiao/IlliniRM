import socket
import numpy as np
from struct import unpack
from serial import Serial

def clip(ang):
    ang = np.maximum(ang, 45)
    ang = np.minimum(ang, 135)
    return ang

class Agent:
    def __init__(self, port = 2333):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.soc.bind(('', port))
        self.ang = None
        self.ser = Serial('/dev/ttyS0', 115200)
    
    def __del__(self):
        self.soc.close()
        self.ser.close()

    def get_angle(self):
        data, addr = self.soc.recvfrom(15)
        if len(data) != 15:
            return False
        data = unpack('15B', data)
        self.ang = clip(data[:3]).astype(np.uint8)
        self.ang -= 90
        return True

    def send_angle(self):
        if self.ang is None:
            return False
        pitch = self.ang[2]
        yaw = self.ang[0]
        l = self.ser.write([90, pitch, yaw])
        if l == 3:
            return True
        else:
            return False

    def pass_over(self):
        ret = self.get_angle()
        if not ret:
            return False
        ret = self.send_angle()
        if not ret:
            return False
        return True
