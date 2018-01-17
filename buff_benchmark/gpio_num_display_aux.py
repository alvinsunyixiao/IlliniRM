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

AUX_BOARD_FIRST_digit_pins = [13, 15, 16, 18, 22, 29, 31]
AUX_BOARD_SECOND_digit_pins = [32, 33, 35, 36, 37, 38, 40]

_SERVER_REMOTE_ADDRESS = "127.0.0.1"
_SERVER_LOCAL_ADDRESS = "127.0.0.1"
_SERVER_PORT = 14000

aux_board_pinout = [AUX_BOARD_FIRST_digit_pins, AUX_BOARD_SECOND_digit_pins]

class third_and_fourth_digit:
    def __init__(self, pos):
        pos -= 3
        self.digit_pinout = aux_board_pinout[pos]
        for i in self.digit_pinout:
            gpio.setup(i, gpio.OUT)

    def show_num(self, num): #hints! 0 for all_off and 8 for all_on
        binary_opt = digit_display[num]
        for i in range(7):
            gpio.output(self.digit_pinout[i], binary_opt[i])

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((_SERVER_LOCAL_ADDRESS, _SERVER_PORT))
    s.listen(1)
    sock, addr = s.accept()
    third_digit = third_and_fourth_digit(3)
    fourth_digit = third_and_fourth_digit(4)
    while True:
        data = sock.recv(1024) #data example: 5|9
        if data:
            data = data.split('|')
            data = [int(i) for i in data]
            third_digit.show_num(data[0])
            fourth_digit.show_num(data[1])

if __name__ == '__main__':
    main()
