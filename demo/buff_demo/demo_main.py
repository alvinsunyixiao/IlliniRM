import caffe
import cv2
import numpy as np
import grid_detect
import time
from collections import Counter
from pprint import pprint
import gpio_num
import os
from IPython import embed

BATCHSIZE = 9

RED_RECORD_PATH = "/tmp/red_record.txt"

try:
    os.remove(RED_RECORD_PATH)
except:
    pass

# Load caffe model
#caffe.set_mode_cpu()
caffe.set_mode_gpu()
caffe.set_device(0)

net = caffe.Net('./model/lenet.prototxt',
                './model/mnist_iter_200000.caffemodel',
               caffe.TEST)
net.blobs['data'].reshape(BATCHSIZE, 1, 28, 28)

gnum = gpio_num.gpio_num_output()
cap = cv2.VideoCapture("nvcamerasrc ! video/x-raw(memory:NVMM), width=(int)640, height=(int)360,format=(string)I420, framerate=(fraction)60/1 ! nvvidconv flip-method=0 ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink")

def read_record(RED_RECORD_PATH):
    try:
        f = open(RED_RECORD_PATH)
        a = f.read()
        f.close()
        a = a.split('\n')
        prv_seq = a[0].split('|')[:-1]
        return [int(i) for i in prv_seq], int(a[1])
    except IOError:
        return None, None

def update_record(white_number_record, red_number_record, input_sequence = None, red_number_sequence = None):
    if input_sequence:
        for n in range(len(input_sequence)): #possibly biased result but more tolerant to low fps
            white_number_record[n].append(input_sequence[n])
    if red_number_sequence:
        for n in range(len(red_number_sequence)): #same; if want more accurate result use range(5)
            red_number_record[n].append(red_number_sequence[n])

def calculate_position_2_hit(white_number_record, red_number_record, prv_red_seq, prv_hit_round):
    if len(white_number_record[0]) == 0 or len(red_number_record[0]) == 0:
        print "YOU RECOGNIZED NOTHING!!! SHAME ON YOU!!!"
        return -1
    final_white_seq = []
    for i in range(9):
        final_white_seq.append(Counter(white_number_record[i]).most_common(1)[0][0])
    final_red_seq = []
    for i in range(5):
        final_red_seq.append(Counter(red_number_record[i]).most_common(1)[0][0])
    print "final_white_seq:"
    print final_white_seq
    print "final red seq: "
    print final_red_seq
    print "prv round:"
    print prv_hit_round
    if not prv_red_seq and not prv_hit_round: #New round
        cur_round = 0
    elif final_red_seq == prv_red_seq: #Had it correct; continue to next round
        cur_round = prv_hit_round + 1
    else: #Had it wrong; let's have a new start
        cur_round = 0
    write_record(final_red_seq, cur_round)
    return final_white_seq.index(final_red_seq[cur_round])

def write_record(seq_2_write, trial_num):
    global RED_RECORD_PATH
    f = open(RED_RECORD_PATH, "w")
    line1 = ""
    for i in seq_2_write:
        line1 += str(i) + "|"
    f.write(line1)
    f.write('\n')
    f.write(str(trial_num))
    f.close()

def main():
    #cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture("nvcamerasrc ! video/x-raw(memory:NVMM), width=(int)640, height=(int)360,format=(string)I420, framerate=(fraction)60/1 ! nvvidconv flip-method=0 ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink")
    while True:
        red_number_record = [[] for i in range(5)]
        white_number_record = [[] for i in range(9)]
        prv_red_seq, prv_hit_round = read_record(RED_RECORD_PATH)
        if prv_hit_round == 4: #WE HAD FINISHED ALL BEFORE
            prv_red_seq = None
            prv_hit_round = None
        raw_input("Press to go")
        #gogogogo
        timer = time.time()
        while time.time() - timer < 0.8:
            ret, img = cap.read()
            cv2.imwrite("debug_5.jpg", img)
            img = cv2.resize(img, (640, 360))
            cv2.imshow('go', img)
            #vout.write(img)
            #vout.write(img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            nine_digit_white_seq, five_digit_red_seq = grid_detect.process(img, net)
            #print nine_digit_white_seq, five_digit_red_seq
            if nine_digit_white_seq != -1:
                if len(nine_digit_white_seq) > 9:
                    nine_digit_white_seq = nine_digit_white_seq[:9]
                update_record(white_number_record, red_number_record, input_sequence = nine_digit_white_seq)
            if five_digit_red_seq != -1:
                if len(five_digit_red_seq) > 5:
                    five_digit_red_seq = five_digit_red_seq[:5]
                update_record(white_number_record, red_number_record, red_number_sequence = five_digit_red_seq)

        pprint(white_number_record)
        pprint(red_number_record)
        try:
            pos = calculate_position_2_hit(white_number_record, red_number_record, prv_red_seq, prv_hit_round)
            #print pos
            gnum.output_num(pos)
        except IndexError:
            print "IndexError. There is at least one digit that can't be recognized"

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        del gnum
        cap.release()
