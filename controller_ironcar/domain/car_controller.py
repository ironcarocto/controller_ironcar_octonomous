from abc import ABCMeta, abstractmethod

class CarController:
    __metaclass__ = ABCMeta

    @abstractmethod
    def set_direction(self, direction):
        raise NotImplementedError

    @abstractmethod
    def set_speed(self, speed):
        raise NotImplementedError

    @abstractmethod
    def stop_car(self):
        raise NotImplementedError
