import logging
import time
from argparse import ArgumentParser
from collections import deque
from math import tan, pi
from os.path import isfile

import numpy as np
import os

import sys

from controller_ironcar.capture import build_capture
from controller_ironcar import CONTROLLER_IRONCAR_PACKAGE_DIR
from controller_ironcar.domain.car_controller import CarController
from controller_ironcar.infrastructure.arduino_car_controller import ArduinoCarController

logger = logging.getLogger('controller_ironcar')

try:
    import picamera.array
except ImportError:
    logger.warning("can't import picamera, "
          "you probably should be running this on the IronCar or install the "
          "picamera library")

DEFAULT_RESOLUTION = 240, 176
DEFAULT_HOME = os.path.realpath(os.path.join(os.getcwd(), 'outputs'))
DEFAULT_SPEED = 0.27
DEFAULT_PREVIEW = False
DEFAULT_CAPTURE = False
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_REGRESSION = False

XTREM_DIRECTION_SPEED_COEFFICIENT = 1
DIRECTION_SPEED_COEFFICIENT = 1
STRAIGHT_COEFFICIENT = 1

CROPPED_LINES = 245
IMG_QUEUE_LENGTH = 3


def main():
    kwargs = load_args()
    set_log_level(kwargs)

    logging.info("INPUTS: ")
    logging.info(kwargs)
    run(**kwargs)


def set_log_level(kwargs):
    log_level = getattr(logging, kwargs.pop("loglevel").upper())
    logging.basicConfig(
        format="[%(levelname)s] - %(message)s",
        level=log_level
    )


def load_args():
    parser = ArgumentParser(description='control the OCTONOMOUS OCTOCAR.')
    parser.add_argument('--resolution', '-r', dest='resolution',
                        type=int, nargs=2,
                        default=DEFAULT_RESOLUTION,
                        help='the (width, height) resolution')
    parser.add_argument('--model-path', '-m', dest='path',
                        type=str,
                        default=None,
                        help='absolute path to the model')
    parser.add_argument('--speed', '-s', dest='speed',
                        type=float, default=DEFAULT_SPEED,
                        help='the car speed (ratio to max speed, from 0 to 1)')
    parser.add_argument('--preview', '-p', dest='preview',
                        action='store_true', default=DEFAULT_PREVIEW,
                        help='if given, camera input will be displayed')
    parser.add_argument('--capture-stream', '-c', dest='capture_stream',
                        action='store_true', default=DEFAULT_CAPTURE,
                        help='if given, camera input will be saved to filesystem')
    parser.add_argument('--regression', '-R', dest='regression',
                        action='store_true', default=DEFAULT_REGRESSION,
                        help='if given, '
                             'uses regression instead of classification')
    parser.add_argument('--log-level', '-l', dest='loglevel',
                        type=str, nargs=1,
                        default=DEFAULT_LOG_LEVEL,
                        help='the log level used (from CRITICAL to DEBUG)')

    args = parser.parse_args()
    check_valid_args(parser, args)
    return extract_values(args)


def check_valid_args(parser: ArgumentParser, args: object):
    valid_arguments = True
    if args.path is None:
        valid_arguments = False
        logger.error('--model-path argument is required')

    if args.path is not None and not isfile(args.path):
        valid_arguments = False
        logger.error('model %s must exist' % args.path)

    if not valid_arguments:
        print(parser.format_help())
        sys.exit(1)


def extract_values(args):
    return {
        "resolution": tuple(args.resolution),
        "model_path": args.path,
        "speed": int(400 + 100 * args.speed),
        "preview": args.preview,
        "capture_stream": args.capture_stream,
        "loglevel": args.loglevel,
        "regression": args.regression
    }


def run(resolution, model_path, speed, preview, capture_stream, regression):
    from keras.models import load_model

    # Objects Initialisation
    # Camera
    cam, cam_output, stream = init_cam(resolution)
    # Model
    model = load_model(model_path)
    # Arduino
    car_controller = ArduinoCarController()

    # Start loop
    if preview:
        cam.start_preview()

    capture = build_capture(DEFAULT_HOME, capture_stream)

    timer(seconds=5)
    start_run(stream, car_controller, model, cam_output, capture, speed, regression)


def timer(seconds=5):
    for i in range(seconds, 0, -1):
        logging.info("Starting in {}".format(i))
        time.sleep(1)
    logging.info("GO !")


def init_cam(resolution=(250, 70)):
    cam = picamera.PiCamera(resolution=resolution, framerate=60)
    cam.awb_mode = 'auto'
    cam_output = picamera.array.PiRGBArray(cam, size=resolution)
    stream = cam.capture_continuous(cam_output, format='rgb',
                                    use_video_port=True)
    return cam, cam_output, stream


def start_run(stream, car_controller: CarController, model, cam_output, capture, speed, regression):
    start = time.time()
    pred_queue = deque(maxlen=4)
    img_queue = deque(maxlen=IMG_QUEUE_LENGTH)
    for index_capture, pict in enumerate(stream):
        """
        :type index_capture: int
        """
        try:
            capture.save(rgb_data=pict.array, index_capture=index_capture)
        except Exception as exception:
            logger.warning('capture picture fails to save - index_capture={}'.format(index_capture))
            logger.warning('exception={}'.format(exception))

        try:
            img_queue.append(crop(pict))
            if index_capture % IMG_QUEUE_LENGTH == 0:
                control_car(car_controller, img_queue, model, speed,
                            regression, pred_queue)
            cam_output.truncate(0)
        except KeyboardInterrupt:
            car_controller.stop_car()
            cam_output.truncate(0)
            stop = time.time()
            elapsed_time = stop - start
            logging.info("Image per second: {}".format(index_capture / elapsed_time))
            time.sleep(2)
            break
        except Exception:
            car_controller.stop_car()
            raise

        index_capture += 1


def crop(pict):
    return pict.array[CROPPED_LINES:, :, :]


def control_car(car_controller: CarController, img_queue, model, speed, regression, queue):
    array = img_queue_to_array(img_queue)
    pred = predict(model, array)
    logging.info(pred)

    direction = direction_command_from_pred(pred, regression)
    #direction = smooth_direction(direction, queue)
    logging.info("direction: {}".format(direction))

    #speed = int(speed_control(direction, speed))
    logging.info("speed: {}".format(speed))

    car_controller.set_direction(direction)
    car_controller.set_speed(speed)



def img_queue_to_array(queue):
    return np.array([x for x in queue])


def predict(model, images):
    preds = model.predict(images)
    return np.mean(preds, axis=0)


def direction_command_from_pred(pred, regression=False):
    if regression:
        # See DrawingLayer in road_simulator for the pi / 6 value
        angle = tan(pred * pi / 6)
        angle = max(-45, min(45, angle))

        # Command range is not centered, hence the difference here :
        if angle > 0:
            direction = int(370 + 100 * angle / 45)
        else:
            direction = int(370 + 130 * angle / 45)

    else:
        command = {
            0: 450,
            1: 260,
            2: 410,
            3: 290,
            4: 340
        }
        direction = command[np.argmax(pred)]
    return direction


def smooth_direction(direction, queue: deque):
    queue.appendleft(direction)
    parameters = [0.7, 0.2, 0.05, 0.05]
    return int(np.average(queue, weights=parameters[:len(queue)]))


def speed_control(direction, speed):
    if direction == 470 or direction == 240:
        return speed * XTREM_DIRECTION_SPEED_COEFFICIENT
    elif direction == 420 or direction == 305:
        return speed * DIRECTION_SPEED_COEFFICIENT
    else:
        return speed * STRAIGHT_COEFFICIENT

if __name__ == '__main__':
    main()
