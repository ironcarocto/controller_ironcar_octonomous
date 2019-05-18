import logging
import os
from datetime import datetime
import numpy as np
from PIL import Image

logger = logging.getLogger('controller_ironcar')


class Capture:
    def __init__(self, output_dir: str):
        self._output_dir = output_dir

    def save(self, rbg_data: np.ndarray, index_capture: int) -> None:
        image_png = Image.fromarray(rbg_data, "RGB")
        filepath = os.path.join(self._output_dir,
                                '{name}.png'.format(name=index_capture))
        logger.debug('save camera output filepath={filepath}'.format(filepath=filepath))
        image_png.save(filepath)


def build_capture(path: str) -> Capture:
    date = datetime.now()
    timestamp = (date - datetime(1970, 1, 1)).total_seconds()
    output_dir = os.path.join(path, str(timestamp))
    logger.info("create output_dir={output_dir}".format(output_dir=output_dir))
    os.makedirs(output_dir, mode=555)
    return Capture(output_dir)
