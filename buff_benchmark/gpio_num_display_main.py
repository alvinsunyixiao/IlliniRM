import RPi.GPIO as gpio

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

mainboard_pinout = [mainboard_FIRST_digit_pins, mainboard_SECOND_digit_pins, mainboard_THIRD_digit_pins]

class digit:
    def __init__(self, pos):
        assert pos < 3 and pos >= 0
        self.digit_pinout = mainboard_pinout[pos]
        for i in self.digit_pinout:
            gpio.setup(i, GPIO.OUT)

    def show_num(self, num): #hints! 0 for all_off and 8 for all_on
        binary_opt = digit_display[num]
        for i in range(7):
            gpio.output(self.digit_pinout[i], binary_opt[i])
