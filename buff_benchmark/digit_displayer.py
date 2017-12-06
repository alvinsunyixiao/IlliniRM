from PIL import Image
from copy import deepcopy

_HARDCODED_BOARD_WIDTH = 540
_HARDCODED_BOARD_HEIGHT = 160

class board:
    def __init__(self, scale = 1):
        self.board_width = int(scale * _HARDCODED_BOARD_WIDTH)
        self.board_height = int(scale * _HARDCODED_BOARD_HEIGHT)
        self.digit_width = (self.board_width / 5)
        self.digit_height = self.board_height
        self.black_background = Image.new("RGB", (self.board_width, self.board_height), "black")
        self.digit_list = []
        for i in range(5):
            self.digit_list.append(digit(self.digit_width, self.digit_height))

    def generate(self, sequence):
        assert len(sequence) == 5
        self.current_display = deepcopy(self.black_background)
        for i in range(5):
            self.digit_list[i].digit_update(sequence[i])
            digit_image = self.digit_list[i].generate()
            box = self.location_tuple_calculator(digit_image, i)
            self.current_display.paste(digit_image, box)
        return self.current_display

    def location_tuple_calculator(self, PILimg_object, num_of_digit): #example: image_tuple_calculator(1, 1); starts from upper left corner
        pic_width, pic_height = PILimg_object.size
        assert pic_height <= self.board_height
        left = num_of_digit * self.digit_width
        right = left + pic_width
        upper = 0
        lower = upper + pic_height
        return (left, upper, right, lower)

class digit:
    def __init__(self, digit_width, digit_height, width_scale = 10):
        self.digit_width = digit_width
        self.digit_height = digit_height
        self.tube_width = int(digit_height / width_scale)
        self.tube_lower_bound = self.tube_width * 1
        self.tube_upper_bound = self.digit_height - self.tube_lower_bound
        self.tube_left_bound = self.tube_width * 1
        self.tube_right_bound = self.digit_width - self.tube_left_bound
        self.tube_length = self.tube_right_bound - self.tube_left_bound - 2 * self.tube_width
        self.black_background = Image.new("RGB", (self.digit_width, self.digit_height), "black")
        self.tube_list = [] #0left1, 1left2, 2right1, 3right2, 4middle1, 5middle2, 6middle3
        for i in range(7):
            self.tube_list.append(tube(self.tube_width, self.tube_length))

    def digit_update(self, desired_digit):
        self.all_off()
        if desired_digit == 1:
            self.tube_list[2].red_on()
            self.tube_list[3].red_on()
        elif desired_digit == 2:
            self.tube_list[4].red_on()
            self.tube_list[2].red_on()
            self.tube_list[5].red_on()
            self.tube_list[1].red_on()
            self.tube_list[6].red_on()
        elif desired_digit == 3:
            self.tube_list[4].red_on()
            self.tube_list[5].red_on()
            self.tube_list[6].red_on()
            self.tube_list[3].red_on()
            self.tube_list[2].red_on()
        elif desired_digit == 4:
            self.tube_list[0].red_on()
            self.tube_list[5].red_on()
            self.tube_list[2].red_on()
            self.tube_list[3].red_on()
        elif desired_digit == 5:
            self.tube_list[4].red_on()
            self.tube_list[0].red_on()
            self.tube_list[5].red_on()
            self.tube_list[3].red_on()
            self.tube_list[6].red_on()
        elif desired_digit == 6:
            self.tube_list[4].red_on()
            self.tube_list[0].red_on()
            self.tube_list[1].red_on()
            self.tube_list[5].red_on()
            self.tube_list[6].red_on()
            self.tube_list[3].red_on()
        elif desired_digit == 7:
            self.tube_list[2].red_on()
            self.tube_list[3].red_on()
            self.tube_list[4].red_on()
        elif desired_digit == 8:
            self.all_on()
        elif desired_digit == 9:
            self.all_on()
            self.tube_list[1].gray_off()
        elif desired_digit == 0:
            self.all_on()
            self.tube_list[5].gray_off()
        else:
            pass

    def all_off(self):
        for i in self.tube_list:
            i.gray_off()

    def all_on(self):
        for i in self.tube_list:
            i.red_on()

    def generate(self):
        digit_display = deepcopy(self.black_background)
        lower_end = 0
        for i in range(7):
            tube_image = self.tube_list[i].generate()
            width, height = tube_image.size
            if i < 2: #left
                left = self.tube_left_bound
                right = left + width
                upper = i * self.tube_length + self.tube_lower_bound + (i + 1) * self.tube_width
                lower = upper + height
                digit_display.paste(tube_image, (left, upper, right, lower))
                if i == 1: lower_end = lower
            elif i < 4: #right
                right = self.tube_right_bound
                left = right - width
                upper = (i - 2) * self.tube_length + self.tube_lower_bound + (i - 1) * self.tube_width
                lower = upper + height
                digit_display.paste(tube_image, (left, upper, right, lower))
            else: #middle
                tube_image = tube_image.transpose(Image.ROTATE_90)
                width, height = tube_image.size
                left = int(self.tube_right_bound - self.tube_left_bound - self.tube_width * 2 - self.tube_length) / 2 + self.tube_left_bound + self.tube_width
                right = left + width
                #rough approx for upper; may cause unwanted shifts when operating on small scale
                if i != 6:
                    upper = (i - 4) * self.tube_length + self.tube_lower_bound + (i - 3) * int(self.tube_width * 0.5)
                else:
                    upper = self.tube_upper_bound - height + 1
                    #upper = lower_end - self.tube_width / 2 - 1
                lower = upper + height
                digit_display.paste(tube_image, (left, upper, right, lower))
        return digit_display

class tube:
    def __init__(self, tube_width, tube_length):
        self.tube_width = tube_width
        self.tube_length = tube_length
        #vertical strip
        self.current_color = "gray"

    def red_on(self):
        #self.current_color = "red"
        self.current_color = (255, 40, 40)

    def gray_off(self):
        self.current_color = (50, 50, 50)

    def generate(self):
        return Image.new("RGB", (self.tube_width, self.tube_length), self.current_color)
