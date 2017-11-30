import caffe
import numpy as np
import cv2
from scipy.ndimage.interpolation import shift


def invert(img, prob = 0.5):
    if np.random.rand() < prob:
        return 1 - img
    else:
        return img

def scale(img, rng):
    assert len(rng) == 2, "range value has exactly two boundary numbers"
    assert rng[1] >= rng[0], "if range arugment, upper bound must be greater than lower bound"
    sc = (rng[1] - rng[0]) * np.random.rand() + rng[0]
    old_s = img.shape[0]
    low_half = img.shape[0] // 2
    up_half = img.shape[0] - low_half
    new_s = int(img.shape[0] * sc)
    if sc >= 1:
        new_s = int(img.shape[0] * sc)
        img = cv2.resize(img, (new_s, new_s))
        mid = new_s // 2
        low = mid - low_half
        high = mid + up_half
        new_img = img[low:high, low:high]
    else:
        new_s = int(img.shape[0] / sc)
        new_img = np.zeros((new_s, new_s), dtype='float32')
        mid = new_s // 2
        low = mid - low_half
        high = mid + up_half
        new_img[low:high, low:high] = img
        new_img = cv2.resize(new_img, (old_s, old_s))
    return new_img, sc

def translate(img, rng, scale):
    assert len(rng) == 2, "range value has exactly two boundary numbers"
    assert rng[1] >= rng[0], "if range arugment, upper bound must be greater than lower bound"
    factor = 1 / scale
    rng[0] *= factor
    rng[1] *= factor
    x = (rng[1] - rng[0]) * np.random.rand() + rng[0]
    y = (rng[1] - rng[0]) * np.random.rand() + rng[0]
    return shift(img, [x,y])

def rotate(img, rng):
    assert len(rng) == 2, "range value has exactly two boundary numbers"
    assert rng[1] >= rng[0], "if range arugment, upper bound must be greater than lower bound"
    ang = (rng[1] - rng[0]) * np.random.rand() + rng[0]
    rows, cols = img.shape
    M = cv2.getRotationMatrix2D((cols/2,rows/2),ang,1)
    dst = cv2.warpAffine(img,M,(cols,rows))
    return dst

def contrast(img, max_rate):
    dif = 0.5 - img
    rate = np.random.rand() * max_rate
    img += dif * rate
    return img

def addnoise(img, max_std):
    std = np.random.rand() * max_std
    noise = np.random.normal(0, std, img.shape)
    return img + noise

def doAugmentation(img,
                   min_rot = -15,
                   max_rot = 15,
                   min_scale = 0.6,
                   max_scale = 1.4,
                   min_translate = -3,
                   max_translate = 3,
                   invert_prob = 0.5,
                   max_contrast = 0.6,
                   max_noise = 0.08):
    img = rotate(img, [min_rot, max_rot])
    img, sc = scale(img, [min_scale, max_scale])
    img = translate(img, [min_translate, max_translate], sc)
    img = invert(img, invert_prob)
    img = contrast(img, max_contrast)
    img = addnoise(img, max_noise)
    return img

class MnistAugmentationLayer(caffe.Layer):

    def setup(self, bottom, top):
        assert len(bottom) == 1, "requires exactly one input"
        assert len(top) == 1, "requires exactly one output"

    def reshape(self, bottom, top):
        top[0].reshape(*bottom[0].data.shape)
        self.params = eval(self.param_str)

    def forward(self, bottom, top):
        top[0].data[...] = bottom[0].data[...]
        for idx in range(top[0].data.shape[0]):
            im = top[0].data[idx,0,:,:]
            top[0].data[idx,0,:,:] = doAugmentation(im,
                                                    self.params['min_rotation'],
                                                    self.params['max_rotation'],
                                                    self.params['min_scale'],
                                                    self.params['max_scale'],
                                                    self.params['min_translation'],
                                                    self.params['max_translation'],
                                                    self.params['invert_probability'],
                                                    self.params['max_contrast'],
                                                    self.params['max_noise'])

    def backward(self, top, propagate_down, bottom):
        pass
