
class GPIO:
    IN = 1
    OUT = 0
    HIGH = 1
    LOW = 0

    def __init__(self, pin):
        with open('/sys/class/gpio/export', 'w') as f:
            f.write('{}'.format(pin))
        self.pin = pin
        self.direction = None

    def __del__(self):
        with open('/sys/class/gpio/unexport', 'w') as f:
            f.write('{}'.format(self.pin))

    def __repr__(self):
        if self.direction is None:
            return 'Pin #{} mode unset'.format(self.pin)
        if self.direction == self.IN:
            return 'Pin #{} in read mode'.format(self.pin)
        elif self.direction == self.OUT:
            return 'Pin #{} in write mode'.format(self.pin)

    def pin_mode(self, direction):
        with open('/sys/class/gpio/gpio{}/direction'.format(self.pin), 'w') as f:
            if direction == self.IN:
                f.write('in')
            elif direction == self.OUT:
                f.write('out')
        self.direction = direction

    def write(self, val):
        with open('/sys/class/gpio/gpio{}/value'.format(self.pin), 'w') as f:
            f.write(str(val))
        self.val = val
