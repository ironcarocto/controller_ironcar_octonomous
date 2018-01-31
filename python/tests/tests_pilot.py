from unittest.mock import MagicMock

import numpy as np

from python.ironcar.car import Car
from python.ironcar.driving_model import DrivingModel
from python.ironcar.driving_modes import AllDrivingModes
from python.ironcar.pilot import Pilot


def create_mock_car_and_pilot():
    logger = MagicMock()
    socket = MagicMock()
    model = MagicMock()
    graph = MagicMock()
    camera = MagicMock()
    memory = MagicMock()

    driving_model = DrivingModel(models_path=".", logger=logger,
                                 model=model, graph=graph)
    car = Car("started", True, car_control=MagicMock(), logger=logger)

    pilot = Pilot(car,
                  visual_input=camera,
                  driving_modes=AllDrivingModes(socket, car,
                                                driving_model, memory),
                  message_stream=socket)
    return pilot, car


class TestCar:

    def test_pilot_with_default_strategy_should_do_nothing(self):
        # Given
        pilot, car = create_mock_car_and_pilot()
        car_control = MagicMock()
        car.car_control = car_control
        input_image = np.random.rand(2, 3, 4)

        # When
        pilot.drive_from_image(input_image)

        # Then
        car_control.set_speed.assert_not_called()
        car_control.set_direction.assert_not_called()
        car_control.stop.assert_not_called()
        car_control.brake.assert_not_called()
        car_control.straight_dir.assert_not_called()

    def test_autopilot_strategy_should_set_speed_and_direction(self):
        # Given
        pilot, car = create_mock_car_and_pilot()
        car_control = MagicMock()
        car.car_control = car_control

        pilot.switch_mode("auto")
        pilot.current_pilot_mode.driving_model.model_loaded = True
        car.start()
        model = pilot.current_pilot_mode.driving_model.model
        model.predict.return_value = [[0, 1]]
        input_image = np.random.rand(2, 3, 4)

        # When
        pilot.drive_from_image(input_image)

        # Then
        car_control.set_direction.assert_called()
        car_control.set_speed.assert_called()

    def test_autodir_strategy_should_set_direction_only(self):
        # Given
        pilot, car = create_mock_car_and_pilot()
        car_control = MagicMock()
        car.car_control = car_control

        pilot.switch_mode("dirauto")
        pilot.current_pilot_mode.driving_model.model_loaded = True
        car.start()
        model = pilot.current_pilot_mode.driving_model.model
        model.predict.return_value = [[0, 1]]
        input_image = np.random.rand(2, 3, 4)

        # When
        pilot.drive_from_image(input_image)

        # Then
        car_control.set_direction.assert_called()
        car_control.set_speed.assert_not_called()

    def test_mode_training_should_use_memory(self):
        # Given
        pilot, car = create_mock_car_and_pilot()
        pilot.switch_mode("training")
        car.start()
        input_image = np.random.rand(2, 3, 4)

        # When
        pilot.drive_from_image(input_image)

        # Then
        pilot.current_pilot_mode.memory.save.assert_called_once()
