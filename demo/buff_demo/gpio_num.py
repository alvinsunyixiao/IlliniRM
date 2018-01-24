import gpio
import sys
import time

GPIO_PIN = [398, 298, 389, 388]

match_output = {
	0: (0, 0, 0, 0),
	1: (0, 0, 0, 1),
	2: (0, 0, 1, 0),
	3: (0, 0, 1, 1),
	4: (0, 1, 0, 0),
	5: (0, 1, 0, 1),
	6: (0, 1, 1, 0),
	7: (0, 1, 1, 1),
	8: (1, 0, 0, 0),
	9: (1, 0, 0, 1)
}

INTERRUPT = (1, 1, 1, 0)

class gpio_num_output:
    def __init__(self):
        self.pin_output = [gpio.GPIO(i) for i in GPIO_PIN]
        for i in self.pin_output:
            i.pin_mode(0)
        self._WRITE_TUPLE_2_PIN(INTERRUPT)

    def __del__(self):
        while (len(self.pin_output) > 0):
            del self.pin_output[0]

    def _WRITE_TUPLE_2_PIN(self, _array):
        assert len(_array) == 4
        for i in range(4):
            self.pin_output[i].write(_array[i])

    def output_num(self, num):
        try:
            output = match_output[num]
        except KeyError:
            print "WRONG INPUT TO gpio_num.py !!!!!!!"
            sys.exit(0)
        self._WRITE_TUPLE_2_PIN(output)
        time.sleep(0.02)
        self._WRITE_TUPLE_2_PIN(INTERRUPT)
