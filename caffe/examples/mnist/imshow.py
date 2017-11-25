import cv2
from caffe.proto.caffe_pb2 import Datum
import numpy as np
import lmdb
from IPython import embed

env = lmdb.open('./mnist_test_lmdb')
with env.begin() as txn:
    raw_data = txn.get(b'00000000')

datum = Datum.FromString(raw_data)
img = np.fromstring(datum.data, dtype=np.uint8)

embed()
