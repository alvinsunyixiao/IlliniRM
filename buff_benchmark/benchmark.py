import os
import matplotlib.pyplot as plt
import matplotlib as mpl
from PIL import Image
from copy import deepcopy
import random
import time

all_image_dir = '2016_img/'

#variables transform constants hardwired to 3x3
_resolution_width = 1920
_resolution_height = 1080
_image_width = int((3 / 13.0) * _resolution_width)
_image_height = int((1 / 4.6) * _resolution_height)
_horizon_black_strip_width = int(0.4 * _image_height)
_vertical_black_strip_width = int(_image_width / 3.0)
black_background = Image.new("RGB", (_resolution_width, _resolution_height), "black")
pause_white_background = Image.new("RGB", (_resolution_width, _resolution_height), "white")

def image_tuple_calculator(PILimg_object, row, col): #example: image_tuple_calculator(1, 1); starts from upper left corner
    width, height = PILimg_object.size
    left = col * _vertical_black_strip_width + (col - 1) * _image_width
    right = left + width
    upper = row * _horizon_black_strip_width + (row - 1) * _image_height
    lower = upper + height
    return _sanity_check((left, upper, right, lower))

def _sanity_check(a_tuple): #do nothing for now.
    return a_tuple

def random_image_selector(desired_number, desire_width, desire_height):
    image_file_path = all_image_dir + str(desired_number) + '/' + str(random.randrange(1, 97)) + '.jpg'
    im = Image.open(image_file_path)
    im = im.resize((desire_width, desire_height))
    return im

def main():
    mpl.rcParams['toolbar'] = 'None'
    fig = plt.figure()
    #fig.canvas.toolbar.pack_forget()
    ax = fig.add_subplot(111)
    ax.set_frame_on(False) #remove white frame
    ax.get_xaxis().set_visible(False) # remove axis and ticks
    ax.get_yaxis().set_visible(False)
    plt.tight_layout(pad=0) #remove padding
    mng = plt.get_current_fig_manager()
    #fig.canvas.window().statusBar().setVisible(False)
    plt.ion()
    plt.show()
    while True:
        available_number = range(1, 10)
        current_round_image = deepcopy(black_background)
        answer = []
        for cur_row in range(1, 4):
            for cur_col in range(1, 4):
                jackpot_number = random.choice(available_number)
                available_number.remove(jackpot_number)
                answer.append(jackpot_number)
                number_image = random_image_selector(jackpot_number, desire_width = _image_width, desire_height = _image_height)
                box = image_tuple_calculator(number_image, cur_row, cur_col)
                current_round_image.paste(number_image, box)
        show(ax, current_round_image)
        print(answer)
        raw_input('Press anykey to continue...')
        show(ax, pause_white_background)
        plt.pause(2)


def show(ax, image_object): #take a ax and an image object (can be numpy, image, plt_image, image...)
    img = ax.imshow(image_object)

if __name__ == '__main__':
    main()
    raw_input('Press anykey to exit...')
