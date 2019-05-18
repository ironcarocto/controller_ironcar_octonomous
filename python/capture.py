import numpy as np
import os
from PIL import Image


class Capture:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def save(self, rbg_data: np.ndarray, index_capture: int):
        image_png = Image.fromarray(rbg_data, "RGB")
        filepath = os.path.join(self.output_dir,
                                '{name}.png'.format(name=index_capture))
        image_png.save(filepath)
