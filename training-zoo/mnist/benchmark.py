import numpy as np
import cv2
import caffe
from IPython import embed
import os
import sys

caffe.set_mode_cpu()

net = caffe.Net('./lenet.prototxt',
                sys.argv[1],
                caffe.TEST)

net.blobs['data'].reshape(1,1,28,28)

path = '../../buff_benchmark/2016_img'

for i in range(1,10):
    ip = os.path.join(path, '{}'.format(i))
    for fn in os.listdir(ip):
        img = cv2.imread(os.path.join(ip,fn))
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        img = cv2.resize(img, (28,28))
        img = img.astype('float32') / 255
        img = 1 - img
        img = img[None,None,...]
        net.blobs['data'].data[...] = img#.astype('float32') / 255
        out = net.forward()
        dig_id = out['prob'].argmax()
        if dig_id != i:
            print(os.path.join(ip,fn))


