_RUN_ON_RPI = True

import os
import sys
import cv2
import numpy as np
from copy import deepcopy
import random
import time
if _RUN_ON_RPI:
    import gpio_num_display_main as gpio_display
import buff_benchmark_comm

all_image_dir = '2016_img/'
_USE_SOCKET = False

#TODO: 1. fix matplotlib on r pi or swtich to cv2. 2. see TODO below
#variables transform constants hardcoded for 3x3
_resolution_width = 1920
_final_resolution_height = 1080
_digit_board_height = 160

#_digit_board_height = int(0.1455 * _final_resolution_height)
#_resolution_height = _final_resolution_height - _digit_board_height
_resolution_height = _final_resolution_height
_image_width = int((3 / 13.0) * _resolution_width) #443
_image_height = int((1 / 4.6) * _resolution_height) #234
#_image_height = int(0.451 * _image_width)
_horizon_black_strip_width = int(0.4 * _image_height) #93
_vertical_black_strip_width = int(_image_width / 3.0) #147
black_background = np.zeros((_resolution_height, _resolution_width), np.uint8)
all_white_background = np.ones((_final_resolution_height, _resolution_width), np.uint8)
all_white_background *= 255 #for displaying

def image_tuple_calculator(cv_obj, row, col): #example: image_tuple_calculator(1, 1); starts from upper left corner
    (height, width) = cv_obj.shape
    left = col * _vertical_black_strip_width + (col - 1) * _image_width
    right = left + width
    upper = row * _horizon_black_strip_width + (row - 1) * _image_height
    lower = upper + height
    return _sanity_check((left, upper, right, lower))

def _sanity_check(a_tuple): #do nothing for now.
    return a_tuple

def random_image_selector(desired_number, desire_width, desire_height):
    image_file_path = all_image_dir + str(desired_number) + '/' + str(random.randrange(1, 97)) + '.jpg'
    im = cv2.imread(image_file_path, 0)
    im = cv2.resize(im, (desire_height, desire_width), 0, 0, cv2.INTER_NEAREST)
    return im

def random_sequence_generator(start, end, desired_length):
    assert desired_length <= end - start
    available_num = range(start, end)
    ret = []
    for i in range(desired_length):
        selected_number = random.choice(available_num)
        available_num.remove(selected_number)
        ret.append(selected_number)
    return ret

def main():
    if _USE_SOCKET:
        print "Waiting for incoming connection to start..."
        benchmark_server = buff_benchmark_comm.server()
    if _RUN_ON_RPI:
        sequence_board = gpio_display.board()
    round_count = 0
    raw_input("Press anykey to start")
    while True:
        available_number = range(1, 10)
        current_round_image = deepcopy(black_background)
        answer = []
        for cur_row in range(1, 4):
            for cur_col in range(1, 4):
                jackpot_number = random.choice(available_number)
                available_number.remove(jackpot_number)
                answer.append(jackpot_number)
                number_image = random_image_selector(jackpot_number, desire_width = _image_height, desire_height = _image_width) #reverse for cv for some reason
                #print "_image_height" + str(_image_height)
                #print "num_img height" + str(number_image.shape[1])
                box = image_tuple_calculator(number_image, cur_row, cur_col)
                #(small_width, small_height) = number_image.shape
                #print box
                #print number_image.shape
                #cv2.imwrite("debug.jpg", number_image)
                current_round_image[box[1]:box[3], box[0]:box[2]] = number_image
                #current_round_image[box[0]:box[2], box[1]:box[3]] = number_image
        current_round_buff_displayer_image = current_round_image
        #current_round_buff_displayer_image = deepcopy(all_white_background)
        #current_round_buff_displayer_image.paste(current_round_image, (0, 0, _resolution_width, _final_resolution_height))
        if round_count % 5 == 0: red_board_sequence = random_sequence_generator(1, 10, 5)
        if _RUN_ON_RPI:
            sequence_board.show_sequence(red_board_sequence)
        #current_round_board_image = sequence_board.generate(red_board_sequence)
        #board_width, board_height = current_round_board_image.size
        #board_left_bound = (_resolution_width - board_width) / 2
        #current_round_buff_displayer_image.paste(current_round_board_image, (board_left_bound, 0, board_left_bound + board_width, _digit_board_height))
        show(current_round_buff_displayer_image)
        #print "showing"
        #plt.pause(0.01)
        cur_time = time.time()
        if _USE_SOCKET:
            benchmark_server.update(answer, red_board_sequence)
            while time.time() - cur_time < 1.5 and not benchmark_server.is_current_round_answered():
                time.sleep(0.1)
        else:
            while time.time() - cur_time < 1.5:
                time.sleep(0.1)
        #print(answer)
        #print(red_board_sequence)
        round_count += 1
        #raw_input('Press anykey to continue...')
        #show(ax, pause_white_background)
        #plt.pause(1)

def show(cv2_img_obj):
    cv2.imshow('buff', cv2_img_obj)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        sys.exit(0)

if __name__ == '__main__':
    main()
    raw_input('Press anykey to exit...')
