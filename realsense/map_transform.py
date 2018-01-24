import numpy as np
import math

_resolution_width = 640 #constants. input camera specs.
_resolution_height = 480
_half_width = _resolution_width / 2.0
_half_height = _resolution_height / 2.0
_fov_x = 50 #TODO: needs to be updated. this is FOV angle
_fov_y = 50

class _depth_camera:
    def __init__(self):
        pass #TODO: this should be initialzation of camera input

    def _test(self):
        pass

    '''
    Input
        - x, y: locations of desired pixel in the RGB/Depth channel
        - depth_matrix: depth matrix
    Output
        - (x, y, z): 3-tuple that represents the relative coordinate of a pixel
    '''
    @static
    def _get_cartesian_coord(x, y, depth_matrix):
        distance = _rawdepth_2_milli([depth_matrix[y, x]])
        (theta, phi) = _get_angle(x, y) #theta is CCW angle from +x (i.e. the direction the camera is facing); Phi is angle from ZY plane
        ret_x = distance
        ret_y = distance * math.tan(theta)
        ret_z = distance * math.tan(-phi + math.pi / 2.0)
        return (ret_x, ret_y, ret_z)

    @static
    def _rawdepth_2_milli(raw_depth):
        pass

    @static
    def _get_angle(_x, _y): #get the x and y angle of the ray (spherical coord. system)
        theta = ((_half_width - _x) / (_half_width)) * (_fov_x / 2)
        phi = math.pi - (((_half_height - _y) / _half_height) * (_fov_y / 2))
        return theta, phi
