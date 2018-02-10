from unittest import TestCase
from unittest.mock import MagicMock

import numpy as np

from simple_command import predict


class TestPredict(TestCase):
    def test_predict_should_return_fine_array(self):
        # Given
        model = MagicMock()
        images = np.random.rand(5, 5, 3)
        model.predict.return_value = np.random.rand(3, 5)

        # When
        result = predict(model, images)

        # Then
        self.assertEqual((5, ), result.shape)
