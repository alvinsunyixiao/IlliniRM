import sys
import socket
import threading
import ast

_SERVER_REMOTE_ADDRESS = "127.0.0.1"
_SERVER_LOCAL_ADDRESS = "127.0.0.1"
_SERVER_PORT = 13003
_TOLERANCE = 10

class client:

    def __init__(self):
        self.current_sequence = [0 for i in range(9)]
        self.continuous_error = 0
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((_SERVER_REMOTE_ADDRESS, _SERVER_PORT))

    def update(self, input_sequence):
        if input_sequence == self.current_sequence:
            self.continuous_error = 0
        else:
            self.continuous_error += 1
            if self.continuous_error >= _TOLERANCE:
                self.current_sequence = input_sequence
                self.continuous_error = 0
                self.send()

    def send(self): #Socket: send sequence to server
        print "Sending Current Sequence: " + str(self.current_sequence)
        self.s.send(str(self.current_sequence))

class server:

    def __init__(self):
        self.current_sequence = [0 for i in range(9)]
        self.current_red_sequence = [0 for i in range(5)]
        self.number_of_sequence_displayed = 0
        self.number_of_right_answers = 0
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
            received_list = ast.literal_eval(data)
            #received_list = [i.strip() for i in received_list]
            if received_list == self.current_sequence:
                self.number_of_right_answers += 1
                print "You are correct for sequence " + str(self.current_sequence)
                print "Current correction rate: %f" % (float(self.number_of_right_answers) / self.number_of_sequence_displayed)

    def update(self, nine_sequence, red_sequence):
        self.current_sequence = nine_sequence
        self.current_red_sequence = red_sequence
        self.number_of_sequence_displayed += 1
