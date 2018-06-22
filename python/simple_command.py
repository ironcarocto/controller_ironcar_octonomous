import logging
import time
from argparse import ArgumentParser
from collections import deque
from math import tan, pi
from os.path import isfile

import Adafruit_PCA9685
import numpy as np

try:
    import picamera.array
except ImportError:
    print("Can't import picamera, "
          "you probably should be running this on the IronCar or install the "
          "picamera library")

DEFAULT_RESOLUTION = 240, 176
DEFAULT_MODEL_PATH = '/home/pi/ironcar/autopilots/octo240x123_nvidia.hdf5'
DEFAULT_SPEED = 0.2
DEFAULT_PREVIEW = False
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_REGRESSION = False

XTREM_DIRECTION_SPEED_COEFFICIENT = 1
DIRECTION_SPEED_COEFFICIENT = 1
STRAIGHT_COEFFICIENT = 1

CROPPED_LINES = 53
IMG_QUEUE_LENGTH = 3


def main():
    kwargs = load_args()
    set_log_level(kwargs)

    logging.info("INPUTS: ")
    logging.info(kwargs)
    run(**kwargs)


def set_log_level(kwargs):
    log_level = getattr(logging, kwargs.pop("loglevel").upper())
    logging.basicConfig(level=log_level)


def load_args():
    parser = ArgumentParser(description='Control the OCTONOMOUS OCTOCAR.')
    parser.add_argument('--resolution', '-r', dest='resolution',
                        type=int, nargs=2,
                        default=DEFAULT_RESOLUTION,
                        help='the (width, height) resolution')
    parser.add_argument('--model-path', '-m', dest='path',
                        type=str,
                        default=DEFAULT_MODEL_PATH,
                        help='absolute path to the model')
    parser.add_argument('--speed', '-s', dest='speed',
                        type=float, default=DEFAULT_SPEED,
                        help='the car speed (ratio to max speed, from 0 to 1)')
    parser.add_argument('--preview', '-p', dest='preview',
                        action='store_true', default=DEFAULT_PREVIEW,
                        help='if given, camera input will be displayed')
    parser.add_argument('--regression', '-R', dest='regression',
                        action='store_true', default=DEFAULT_REGRESSION,
                        help='if given, '
                             'uses regression instead of classification')
    parser.add_argument('--log-level', '-l', dest='loglevel',
                        type=str, nargs=1,
                        default=DEFAULT_LOG_LEVEL,
                        help='the log level used (from CRITICAL to DEBUG)')

    args = parser.parse_args()
    check_valid_args(args)
    return extract_values(args)


def check_valid_args(args):
    assert isfile(args.path), "Model {} must exist".format(args.path)


def extract_values(args):
    return {
        "resolution": tuple(args.resolution),
        "model_path": args.path,
        "speed": int(400 + 100 * args.speed),
        "preview": args.preview,
        "loglevel": args.loglevel,
        "regression": args.regression
    }


def run(resolution, model_path, speed, preview, regression):
    from keras.models import load_model

    # Objects Initialisation
    # Camera
    cam, cam_output, stream = init_cam(resolution)
    # Model
    model = load_model(model_path)
    # Arduino
    pwm = Adafruit_PCA9685.PCA9685()
    pwm.set_pwm_freq(60)

    # Start loop
    if preview:
        cam.start_preview()
    timer(seconds=5)
    start_run(stream, pwm, model, cam_output, speed, regression)


def timer(seconds=5):
    for i in range(seconds, 0, -1):
        logging.info("Starting in {}".format(i))
        time.sleep(1)
    logging.info("GO !")


def init_cam(resolution=(250, 70)):
    cam = picamera.PiCamera(resolution=resolution, framerate=60)
    cam.awb_mode = 'flash'
    cam_output = picamera.array.PiRGBArray(cam, size=resolution)
    stream = cam.capture_continuous(cam_output, format='rgb',
                                    use_video_port=True)
    return cam, cam_output, stream


def start_run(stream, pwm, model, cam_output, speed, regression):
    start = time.time()
    pred_queue = deque(maxlen=4)
    img_queue = deque(maxlen=IMG_QUEUE_LENGTH)
    for i, pict in enumerate(stream):
        try:
            img_queue.append(crop(pict))
            if i % IMG_QUEUE_LENGTH == 0:
                control_car(pwm, img_queue, model, speed,
                            regression, pred_queue)
            cam_output.truncate(0)
        except KeyboardInterrupt:
            stop_car(pwm)
            cam_output.truncate(0)
            stop = time.time()
            elapsed_time = stop - start
            logging.info("Image per second: {}".format(i / elapsed_time))
            time.sleep(2)
            break
        except Exception:
            stop_car(pwm)
            raise


def crop(pict):
    return pict.array[CROPPED_LINES:, :, :]


def control_car(pwm, img_queue, model, speed, regression, queue):
    array = img_queue_to_array(img_queue)
    pred = predict(model, array)
    logging.info(pred)

    direction = direction_command_from_pred(pred, regression)
    direction = smooth_direction(direction, queue)
    logging.info("direction: {}".format(direction))

    speed = int(speed_control(direction, speed))
    logging.info("speed: {}".format(speed))

    pwm.set_pwm(2, 0, direction)
    pwm.set_pwm(1, 0, speed)


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
            0: 470,
            1: 420,
            2: 370,
            3: 305,
            4: 240
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


def stop_car(pwm):
    pwm.set_pwm(1, 0, 400)
    pwm.set_pwm(2, 0, 400)


if __name__ == '__main__':
    main()
