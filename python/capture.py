import logging
import os
from datetime import datetime
import numpy as np
from PIL import Image

logger = logging.getLogger('controller_ironcar')

import threading


class Capture:
    def save(self, rgb_data: np.ndarray, index_capture: int) -> None:
        raise NotImplementedError


class FileSystemCapture(Capture):
    def __init__(self, output_dir: str):
        self._output_dir = output_dir

    def save(self, rgb_data: np.ndarray, index_capture: int) -> None:
        image_png = Image.fromarray(rgb_data, "RGB")
        filepath = os.path.join(self._output_dir,
                                '{name}.png'.format(name=index_capture))
        logger.debug('save camera output filepath={filepath}'.format(filepath=filepath))

        t = threading.Thread(target=image_png.save, args=(filepath,))
        t.start()


class StubCapture(Capture):
    """
    This class is used to create a stub object to ensure we DON'T
    save images when the stream capture is disabled.
    """
    def __init__(self):
        pass

    def save(self, *args, **kwargs) -> None:
        pass


def build_capture(path: str, capture_stream) -> Capture:
    """
    Builds a Capture object, with different properties based on parameters.

    :param path: str, the path of the output directory where images will be saved, if applicable
    :param capture_stream: bool, whether the stream must be saved or not.
    :return: a Capture object
    """
    if not capture_stream:
        return StubCapture()

    date = datetime.now()
    timestamp = (date - datetime(1970, 1, 1)).total_seconds()
    output_dir = os.path.join(path, '{}'.format(timestamp))
    logger.info("create output_dir={output_dir}".format(output_dir=output_dir))
    os.makedirs(output_dir)
    return FileSystemCapture(output_dir)
