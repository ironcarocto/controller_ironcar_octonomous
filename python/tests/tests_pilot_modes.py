from unittest.mock import MagicMock

from python.ironcar.driving_modes import FullAutoPilot


class TestFullAutoPilot:
    def create_autopilot(self):
        self.stream = MagicMock(name="socket")
        self.brain = MagicMock(name="driving_model")
        self.car = MagicMock(name="car")
        self.pilot = FullAutoPilot(self.stream, self.car, self.brain)

    def test_pilot_load_model_should_call_brain_load_model(self):
        # Given
        self.create_autopilot()
        pilot = self.pilot
        model_name = "my_model"

        # When
        _ = pilot.load_model(model_name)

        # Then
        self.brain.load_model.assert_called_once_with(model_name)
