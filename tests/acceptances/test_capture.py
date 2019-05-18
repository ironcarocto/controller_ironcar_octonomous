import numpy as np
import os
from PIL import Image

from python.capture import Capture
from tests.acceptances.fixtures import clone_fixture


def test_save_should_write_a_png_image_from_rgb_data():
    # Given
    result_image_name = "0.png"
    i = 0
    with clone_fixture("image_ironcar") as path:
        img_filename = os.path.join(path, "ironcar.jpg")
        img = Image.open(img_filename)
        img_rgb = img.convert("RGB")
        rgb_array = np.array(img_rgb)
        output_dir = os.path.join(path, "output")
        expected_file_path = os.path.join(output_dir, result_image_name)
        capture = Capture(output_dir)

        # When
        capture.save(rgb_array, i)

        # Then
        assert os.path.isfile(expected_file_path)