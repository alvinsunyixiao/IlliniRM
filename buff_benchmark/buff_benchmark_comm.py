import sys
import socket
import threading
import ast
import os
import time

try:
    os.remove('/tmp/white_correct.txt')
    os.remove('/tmp/red_correct.txt')
    os.remove("/tmp/fps.txt")
    os.remove("/tmp/white_wrong_stats.txt")
    os.remove("/tmp/red_wrong_stats.txt")
except:
    pass

_SERVER_REMOTE_ADDRESS = "127.0.0.1"
_SERVER_LOCAL_ADDRESS = "127.0.0.1"
_MODE = "ALL" #"ALL" for entire sequence input; "SIMUL" for position input
_SERVER_PORT = 13003
_WHITE_NUM_TOLERANCE = 2
_RED_NUM_TOLERANCE = 2
fps_counter = time.time()
frame_elapsed = 0

def _server_plot_helper(to_path, str_2_write):
    f = open(to_path, 'a+')
    f.write(str_2_write)
    f.write('\n')
    f.close()

def element_wise_comparison(iter_1, iter_2):
    assert len(iter_1) == len(iter_2)
    acc = 0
    for i in range(len(iter_1)):
        if iter_1[i] == iter_2[i]: acc += 1
    return acc

def fps_count():
    global fps_counter
    global frame_elapsed
    a = time.time()
    if a - fps_counter >= 1:
        _server_plot_helper("/tmp/fps.txt", str(frame_elapsed))
        fps_counter = a
        frame_elapsed = 0
    else:
        frame_elapsed += 1

class client:

    def __init__(self):
        self.current_sequence = [0 for i in range(9)]
        self.current_red_sequence = [0 for i in range(5)]
        self.continuous_error = 0
        self.red_continuous_error = 0
        self.white_frame_processed = 0 #update per round
        self.red_frame_processed = 0
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((_SERVER_REMOTE_ADDRESS, _SERVER_PORT))

    def update(self, input_sequence = None, red_number_sequence = None):
        '''
        if red_number_sequence:
            if red_number_sequence == self.current_red_sequence:
                self.continuous_red
            if (element_wise_comparison(red_number_sequence, self.current_red_sequence) >= 2 and self.red_continuous_error >= 3) or self.red_continuous_error >= _RED_NUM_TOLERANCE:
                #new round starts

        '''
        fps_count()
        if red_number_sequence:
            if -1 not in red_number_sequence:
                if red_number_sequence == self.current_red_sequence:
                    self.red_continuous_error = 0
                else:
                    self.red_continuous_error += 1
                    if self.red_continuous_error >= _RED_NUM_TOLERANCE:
                        self.current_red_sequence = red_number_sequence
                        self.red_continuous_error = 0
            else:
                self.red_prob_pool_update(red_number_sequence)
        if input_sequence:
            if input_sequence == self.current_sequence:
                self.continuous_error = 0
            else:
                self.continuous_error += 1
                if self.continuous_error >= _WHITE_NUM_TOLERANCE:
                    self.current_sequence = input_sequence
                    self.continuous_error = 0
                    self.send() #New round starts

    def white_prob_pool_update(self, prob_sequence):
        pass

    def red_prob_pool_update(self, uncertain_sequence):
        pass

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
        self.white_wrong_stats = [0 for i in range(10)]
        self.red_wrong_stats = [0 for i in range(10)]
        self.current_round_answered = False
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((_SERVER_LOCAL_ADDRESS, _SERVER_PORT))
        self.s.listen(1)
        self.sock, self.addr = self.s.accept()
        print "Connection established. Starting in 5 seconds"
        self.t = threading.Thread(target = self.handler)
        self.t.start()

    def is_current_round_answered(self):
        return self.current_round_answered

    def handler(self):
        print "Incoming connection from %s:%s" % self.addr
        while True:
            data = self.sock.recv(1024)
            data = data.split("\r\n")
            received_list = ast.literal_eval(data[0])
            received_red_list = ast.literal_eval(data[1])
            #received_list = [i.strip() for i in received_list]
            if received_list:
                self.current_round_answered = True
            if received_list == self.current_sequence and not self.current_round_answered:
                self.number_of_right_answers += 1
                #print "You are correct for sequence " + str(self.current_sequence)
                print "White sequence correct!"
            if received_red_list == self.current_red_sequence:
                self.number_of_red_right_answers += 1
                print "Red sequence correct!"
            if received_list != self.current_sequence:
                self.white_stats_keeper(received_list, self.current_sequence)
            if received_red_list != self.current_red_sequence:
                self.red_stats_keeper(received_red_list, self.current_red_sequence)
            cur_white_rate = float(self.number_of_right_answers) / self.number_of_sequence_displayed
            cur_red_rate = float(self.number_of_red_right_answers) / self.number_of_sequence_displayed
            print "White sequence received: " + str(received_list)
            print "Red sequence received: " + str(received_red_list)
            #print "Current white-num correct detection rate: %f" % cur_white_rate
            #print "Current red-num correct detection rate: %f" % cur_red_rate
            _server_plot_helper('/tmp/white_correct.txt', str(cur_white_rate))
            _server_plot_helper('/tmp/red_correct.txt', str(cur_red_rate))

    def update(self, nine_sequence, red_sequence):
        self.current_sequence = nine_sequence
        self.current_red_sequence = red_sequence
        self.number_of_sequence_displayed += 1
        self.current_round_answered = False
        print "------------------"
        print "New round staaaaart!"
        print "Current white sequence: " + str(self.current_sequence) + "\nCurrent red sequence: " + str(self.current_red_sequence)

    def white_stats_keeper(self, user_input, server_answer):
        assert len(user_input) == len(server_answer)
        for i in range(len(user_input)):
            if user_input[i] != server_answer[i]:
                self.white_wrong_stats[server_answer[i]] += 1
        f = open('/tmp/white_wrong_stats.txt', 'w')
        for i in self.white_wrong_stats:
            f.write(str(i) + '\n')
        f.close()

    def red_stats_keeper(self, user_input, server_answer):
        assert len(user_input) == len(server_answer)
        for i in range(len(user_input)):
            if user_input[i] != server_answer[i]:
                self.red_wrong_stats[server_answer[i]] += 1
        f = open('/tmp/red_wrong_stats.txt', 'w')
        for i in self.red_wrong_stats:
            f.write(str(i) + '\n')
        f.close()
