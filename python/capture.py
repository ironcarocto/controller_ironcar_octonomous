import logging
import os
from datetime import datetime
import numpy as np
from PIL import Image

logger = logging.getLogger('controller_ironcar')


class Capture:
    def __init__(self, output_dir: str):
        self._output_dir = output_dir

    def save(self, rgb_data: np.ndarray, index_capture: int) -> None:
        image_png = Image.fromarray(rgb_data, "RGB")
        filepath = os.path.join(self._output_dir,
                                '{name}.png'.format(name=index_capture))
        logger.debug('save camera output filepath={filepath}'.format(filepath=filepath))
        image_png.save(filepath)


class StubCapture:
    """
    This class is used to create a stub object to ensure we DON'T
    save images when the stream capture is disabled.
    """
    def __init__(self):
        pass

    def save(self, *args, **kwargs) -> None:
        pass


def build_capture(path: str) -> Capture:
    date = datetime.now()
    timestamp = (date - datetime(1970, 1, 1)).total_seconds()
    output_dir = os.path.join(path, '{}'.format(timestamp))
    logger.info("create output_dir={output_dir}".format(output_dir=output_dir))
    os.makedirs(output_dir, mode=777)
    return Capture(output_dir)
