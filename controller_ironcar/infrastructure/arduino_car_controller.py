from controller_ironcar.domain.car_controller import CarController


class ArduinoCarController(CarController):

    def __init__(self):
        import Adafruit_PCA9685
        self._pwm = Adafruit_PCA9685.PCA9685()
        self._pwm.set_pwm_freq(60)

    def set_direction(self, direction):
        self._pwm.set_pwm(2, 0, direction)


    def set_speed(self, speed):
        self._pwm.set_pwm(1, 0, speed)

    def stop_car(self):
        self._pwm.set_pwm(1, 0, 400)
        self._pwm.set_pwm(2, 0, 400)

