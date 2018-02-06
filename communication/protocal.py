from crc8 import crc8
from enum import Enum
from struct import pack

class CMDID(Enum):
    VR_SHOOT = 0x0030

class Encoder:
    HEAD = 'iRM'

    @classmethod
    def header(cls, length):
        rs = cls.HEAD + pack('>H', length)
        return rs

    @classmethod
    def encode(cls, cmdid, data):
        msg = pack('>H', cmdid.value)
        crc = crc8()
        if cmdid == CMDID.VR_SHOOT:
            pitch, yaw, pitch_s, yaw_s = data
            msg += pack('>4f', pitch, yaw, pitch_s, yaw_s)
        header = cls.header(len(msg) + 1)
        crc.update(header)
        header_checksum = crc.digest()
        msg = header_checksum + msg
        crc.update(msg)
        total_checksum = crc.digest()
        return header + msg + total_checksum



