class Car(object):
    def __init__(self, state, running, car_control, logger, curr_direction=0,
                 curr_gas=0, max_speed_rate=0.5):
        self.state = state
        self.running = running
        self.file_count = 0
        self.logger = logger

        self.car_control = car_control
        self.curr_direction = curr_direction
        self.curr_gas = curr_gas
        self.max_speed_rate = max_speed_rate

    def start_or_stop(self, data):
        assert data in ("started", "stopped"), \
            "Passed value should be started or stopped"
        self.state = data
        print('starter set to  ' + data)

    def start(self):
        self.start_or_stop("started")

    def stop(self):
        self.start_or_stop("stopped")

    def set_direction(self, data):
        self.curr_direction = float(data)
        if self.curr_direction == 0:
            self.car_control.straight_dir()
        else:
            self.car_control.set_direction(self.curr_direction)

    def set_gas(self, data):
        if self.state == "started":
            self.curr_gas = float(data) * self.max_speed_rate
        else:
            self.curr_gas = 0

        print('THIS IS THE CURRENT GAS_COMMAND ', self.curr_gas)
        if self.curr_gas < 0:
            self.car_control.brake()
        elif self.curr_gas == 0:
            self.car_control.stop()
        else:
            self.car_control.set_speed(self.curr_gas)

    def set_max_speed(self, new_max_speed):
        self.max_speed_rate = new_max_speed
