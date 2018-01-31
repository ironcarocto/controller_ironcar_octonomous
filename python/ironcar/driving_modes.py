from python.ironcar.memory import Memory


class DrivingModes(object):
    def __init__(self):
        self.modes = {}

    @property
    def mode_names(self):
        return list(self.modes.keys())

    def get(self, mode):
        message = "mode {} is unknown, " \
                  "must be one of {}".format(mode, self.mode_names)
        assert mode in self.modes.keys(), message
        return self.modes[mode]

    def add(self, name, mode):
        self.modes.setdefault(name, mode)
        return self


class AllDrivingModes(DrivingModes):
    def __init__(self, intruction_stream, car, driving_model, memory):
        super().__init__()
        (self
            .add("rest", DefaultDrivingMode(intruction_stream, car))
            .add("dirauto",
                 DirectionOnlyAutoPilot(intruction_stream, car, driving_model))
            .add("auto", FullAutoPilot(intruction_stream, car, driving_model))
            .add("training", LearningPilot(intruction_stream, car, memory)))


class DefaultDrivingMode(object):
    def __init__(self, instructions_stream, car):
        self.car = car
        instructions_stream.on('gas', self.car.set_gas)
        instructions_stream.on('dir', self.car.set_direction)

    def drive(self, img):
        pass

    def load_model(self, model_name):
        pass


class FullAutoPilot(DefaultDrivingMode):
    def __init__(self, instructions_stream, car, driving_model):
        super().__init__(instructions_stream, car)
        self.car = car
        self.driving_model = driving_model
        instructions_stream.off('gas')
        instructions_stream.off('dir')
        message = 'Autopilot mode. ' \
                  'Use the start/stop button to free the gas command.'
        instructions_stream.emit('msg2user', message)

    def drive(self, img):
        direction = self.car.curr_direction

        local_dir, local_gas = self.driving_model.decide_direction_and_gas(img,
                                                                           direction)
        self.car.set_gas(local_gas)
        self.car.set_direction(local_dir)
        return local_dir, local_gas

    def load_model(self, model_name):
        return self.driving_model.load_model(model_name)


class DirectionOnlyAutoPilot(DefaultDrivingMode):
    def __init__(self, instructions_stream, car, driving_model):
        super().__init__(instructions_stream, car)
        self.driving_model = driving_model
        instructions_stream.off('dir')
        message = 'Direction auto mode. ' \
                  'Please control the gas using a keyboard or a gamepad.'
        instructions_stream.emit('msg2user', message)

    def drive(self, img):
        direction = self.car.curr_direction

        local_dir, local_gas = self.driving_model.decide_direction_and_gas(img,
                                                                           direction)
        self.car.set_direction(local_dir)
        return local_dir, local_gas

    def load_model(self, model_name):
        return self.driving_model.load_model(model_name)


class LearningPilot(DefaultDrivingMode):
    def __init__(self, instructions_stream, car, memory: Memory):
        super().__init__(instructions_stream, car)
        self.memory = memory

    def drive(self, img):
        self.memory.save(img, self.car.curr_gas, self.car.curr_direction)
