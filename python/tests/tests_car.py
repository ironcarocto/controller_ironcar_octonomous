from unittest.mock import MagicMock

import pytest

from python.ironcar.driving_model import DrivingModel
from python.ironcar.car import Car
from python.ironcar.driving_modes import AllDrivingModes
from python.ironcar.pilot import Pilot


def create_mock_car_and_pilot():
    logger = MagicMock()
    socket = MagicMock()
    model = MagicMock()
    graph = MagicMock()
    camera = MagicMock()
    memory = MagicMock()

    brain = DrivingModel(models_path=".", logger=logger, model=model,
                         graph=graph)
    car = Car("started", car_control=MagicMock(), logger=logger)
    pilot = Pilot(car,
                  visual_input=camera,
                  driving_modes=AllDrivingModes(socket, car, brain, memory),
                  message_stream=socket)
    return pilot, car


class TestCar:

    def test_on_start_should_apply_data_to_state(self):
        for state in ("started", "stopped"):
            # Given
            data = state
            pilot, car = create_mock_car_and_pilot()

            # When
            car.start_or_stop(data)

            # Then
            assert car.state == data

    def test_on_start_should_raise_AssertionError_if_input_is_invalid(self):
        with pytest.raises(AssertionError):
            # Given
            data = "invalid"
            pilot, car = create_mock_car_and_pilot()

            # When
            car.start_or_stop(data)

    def test_set_gas_changes_current_gas_if_car_is_started(self):
        # Given
        pilot, car = create_mock_car_and_pilot()
        car.start()
        car.set_max_speed(1)

        # When
        car.set_gas(1)

        # Then
        assert car.curr_gas == 1

    def test_set_gas_sets_current_gas_to_zero_if_car_is_stopped(self):
        # Given
        pilot, car = create_mock_car_and_pilot()
        car.stop()

        # When
        car.set_gas(1)

        # Then
        assert car.curr_gas == 0
