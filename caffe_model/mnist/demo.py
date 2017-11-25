import numpy as np
import cv2
import caffe
from IPython import embed

caffe.set_mode_cpu()

net = caffe.Net('./lenet.prototxt',
                './lenet_iter_50000.caffemodel',
                caffe.TEST)

net.blobs['data'].reshape(1,1,28,28)

cap = cv2.VideoCapture(0)

HL = 24

mask = np.zeros((HL*2,HL*2))
cv2.circle(mask, (HL,HL), 12, 1, -1)
mask = mask.astype(bool)
fourcc = cv2.VideoWriter_fourcc(*'MP4V')
vout = cv2.VideoWriter('output.mp4', fourcc, 20.0, (1280,720))

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    crop = frame[360-HL:360+HL, 640-HL:640+HL]
    crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    #crop = cv2.adaptiveThreshold(crop,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #                             cv2.THRESH_BINARY_INV,27,10)
    #crop = cv2.GaussianBlur(crop,(7,7),0)
    #ret, crop = cv2.threshold(crop,0,255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    #crop = cv2.blur(crop, (3,3))
    #dig *= mask
    dig = crop.astype('float32') / 255
    #dig1 = 1 - dig
    dig = cv2.resize(dig, (28,28))
    #thresh = 0.4
    #rate = 0.8
    #low_idx = np.argwhere(dig <= thresh)
    #hi_idx = np.argwhere(dig > thresh)
    #dig[low_idx[:,0],low_idx[:,1]] -= dig[low_idx[:,0],low_idx[:,1]] * rate
    #dig[hi_idx[:,0],hi_idx[:,1]] += (1-dig[hi_idx[:,0],hi_idx[:,0]]) * rate
    img = dig[None,None,...]
    net.blobs['data'].data[...] = img#.astype('float32') / 255
    out = net.forward()
    dig_id = out['prob'].argmax()
    conf = out['prob'][0,dig_id]
    cv2.rectangle(frame, (640-HL, 360-HL), (640+HL, 360+HL),
                  (0, 255, 0), 3)
    cv2.putText(frame,str(dig_id)+' confidence: '+str(conf),
                (640-HL, 360-HL-20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0,255,0),
                2,cv2.LINE_AA)
    # Display the resulting frame
    vout.write(frame)
    cv2.imshow('frame',frame)
    cv2.imshow('digit', dig)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
vout.release()
cv2.destroyAllWindows()
