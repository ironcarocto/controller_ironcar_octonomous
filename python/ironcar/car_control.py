import Adafruit_PCA9685

from conf.utils import load_commands


class CarControl(object):
    _commands = load_commands()
    NEUTRAL_COMMAND = _commands['neutral']
    MAX_COMMAND = _commands['drive_max']
    GAS_COMMAND = _commands['gas']
    STOP_COMMAND = _commands['stop']
    DIRECTION_COMMAND = _commands['direction']
    RIGHT_COMMAND = _commands['right']
    LEFT_COMMAND = _commands['left']
    STRAIGHT_COMMAND = _commands['straight']

    def __init__(self):
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(60)

    def set_direction(self, direction):
        direction_range = (self.RIGHT_COMMAND - self.LEFT_COMMAND) / 2.
        direction_offset = self.STRAIGHT_COMMAND
        direction_value = int(direction * direction_range) + direction_offset
        self.pwm.set_pwm(self.DIRECTION_COMMAND,
                         0,
                         direction_value)

    def straight_dir(self):
        self.pwm.set_pwm(self.DIRECTION_COMMAND, 0, self.STRAIGHT_COMMAND)

    def set_speed(self, gas):
        gas_range = (self.MAX_COMMAND - self.NEUTRAL_COMMAND)
        gas_offset = self.MAX_COMMAND
        power_value = int(gas * gas_range) + gas_offset
        self.pwm.set_pwm(self.GAS_COMMAND, 0, power_value)

    def brake(self):
        self.pwm.set_pwm(self.GAS_COMMAND, 0, self.STOP_COMMAND)

    def stop(self):
        self.pwm.set_pwm(self.GAS_COMMAND, 0, self.NEUTRAL_COMMAND)
