import RPi.GPIO as gpio
import socket

gpio.setmode(gpio.BOARD)

digit_display = {
	0: (0, 0, 0, 0, 0, 0, 0),
	1: (0, 1, 1, 0, 0, 0, 0),
	2: (1, 1, 0, 1, 1, 0, 1),
	3: (1, 1, 1, 1, 0, 0, 1),
	4: (0, 1, 1, 0, 0, 1, 1),
	5: (1, 0, 1, 1, 0, 1, 1),
	6: (1, 0, 1, 1, 1, 1, 1),
	7: (1, 1, 1, 0, 0, 0, 0),
	8: (1, 1, 1, 1, 1, 1, 1),
	9: (1, 1, 1, 1, 0, 1, 1)
}

for i in range(10): #for some unknown reason we need to xor
    digit_display[i] = [j ^ 1 for j in digit_display[i]]

mainboard_FIRST_digit_pins = [3, 5, 7, 8, 10, 11, 12]
mainboard_SECOND_digit_pins = [13, 15, 16, 18, 22, 29, 31]
mainboard_THIRD_digit_pins = [32, 33, 35, 36, 37, 38, 40]

_SERVER_REMOTE_ADDRESS = "127.0.0.1"
_SERVER_LOCAL_ADDRESS = "127.0.0.1"
_SERVER_PORT = 14000

mainboard_pinout = [mainboard_FIRST_digit_pins, mainboard_SECOND_digit_pins, mainboard_THIRD_digit_pins]

class board:
    def __init__(self):
        self.zero = digit(0)
        self.first = digit(1)
        self.second = digit(2)
        self.third_and_fourth = remote_third_and_fourth_digit()
        self.main_board_digit_list = [self.zero, self.first, self.second]

    def show_sequence(self, seq):
        for i in range(4):
            if i == 3:
                self.third_and_fourth.show_num(seq[i], seq[i+1])
            self.main_board_digit_list[i].show_num(seq[i])

class remote_third_and_fourth_digit:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((_SERVER_REMOTE_ADDRESS, _SERVER_PORT))

    def show_num(self, first_num, second_num):
        _send_str = str(first_num) + '|' + str(second_num)
        self.s.send(_send_str)

class digit:
    def __init__(self, pos):
        if pos < 3:
            self.digit_pinout = mainboard_pinout[pos]
            for i in self.digit_pinout:
                gpio.setup(i, gpio.OUT)

    def show_num(self, num): #hints! 0 for all_off and 8 for all_on
        binary_opt = digit_display[num]
        for i in range(7):
            gpio.output(self.digit_pinout[i], binary_opt[i])
