import cv2
import caffe
import numpy as np
import lmdb
from IPython import embed
from caffe.proto.caffe_pb2 import Datum

caffe.set_mode_cpu()

net = caffe.Net('./lenet_train_test.prototxt',
                './lenet_iter_10000.caffemodel',
                caffe.TEST)




embed()
