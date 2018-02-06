import serial
from crc8 import crc8

class UartCom:
    def __init__(self, port, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial = serial.Serial(port, baudrate, timeout=0)

    def __del__(self):
        pass
