import sys
import socket
import threading
import ast

_SERVER_REMOTE_ADDRESS = "127.0.0.1"
_SERVER_LOCAL_ADDRESS = "127.0.0.1"
_SERVER_PORT = 13003
_WHITE_NUM_TOLERANCE = 7
_RED_NUM_TOLERANCE = 9

def _plot_helper(to_path, str_2_write):
    f = open(to_path, 'a+')
    f.write(str_2_write) 
    f.write('\n')
    f.close()

class client:

    def __init__(self):
        self.current_sequence = [0 for i in range(9)]
        self.current_red_sequence = [0 for i in range(5)]
        self.continuous_error = 0
        self.red_continuous_error = 0
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((_SERVER_REMOTE_ADDRESS, _SERVER_PORT))

    def update(self, input_sequence, red_number_sequence, switch1 = False, switch2 = False):
        if input_sequence == self.current_sequence:
            self.continuous_error = 0
        else:
            self.continuous_error += 1
            if self.continuous_error >= _WHITE_NUM_TOLERANCE:
                self.current_sequence = input_sequence
                self.continuous_error = 0
                switch1 = True
        if red_number_sequence == self.current_red_sequence:
            self.continuous_error = 0
        else:
            self.red_continuous_error += 1
            if self.red_continuous_error >= _RED_NUM_TOLERANCE:
                self.current_red_sequence = red_number_sequence
                self.red_continuous_error = 0
                switch2 = True
        if switch1 and switch2:
            self.send()

    def send(self): #Socket: send sequence to server
        print "Sending Current Sequence: " + str(self.current_sequence)
        self.s.send(str(self.current_sequence) + "\r\n" + str(self.current_red_sequence))

class server:

    def __init__(self):
        self.current_sequence = [0 for i in range(9)]
        self.current_red_sequence = [0 for i in range(5)]
        self.number_of_sequence_displayed = 0
        self.number_of_right_answers = 0
        self.number_of_red_right_answers = 0
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((_SERVER_LOCAL_ADDRESS, _SERVER_PORT))
        self.s.listen(1)
        self.sock, self.addr = self.s.accept()
        self.t = threading.Thread(target = self.handler)
        self.t.start()

    def handler(self):
        print "Incoming connection from %s:%s" % self.addr
        while True:
            data = self.sock.recv(1024)
            data = data.split("\r\n")
            received_list = ast.literal_eval(data[0])
            received_red_list = ast.literal_eval(data[1])
            #received_list = [i.strip() for i in received_list]
            if received_list == self.current_sequence:
                self.number_of_right_answers += 1
                #print "You are correct for sequence " + str(self.current_sequence)
            if received_red_list == self.current_red_sequence:
                self.number_of_red_right_answers += 1
            cur_white_rate = float(self.number_of_right_answers) / self.number_of_sequence_displayed
            cur_red_rate = float(self.number_of_red_right_answers) / self.number_of_sequence_displayed
            print "Current white-num correction rate: %f" % cur_white_rate
            print "Current red-num correction rate: %f" % cur_red_rate
            _plot_helper('/tmp/white_correct.txt', str(cur_white_rate))
            _plot_helper('/tmp/red_correct.txt', str(cur_red_rate))

    def update(self, nine_sequence, red_sequence):
        self.current_sequence = nine_sequence
        self.current_red_sequence = red_sequence
        self.number_of_sequence_displayed += 1
