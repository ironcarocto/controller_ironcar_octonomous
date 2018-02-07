# Import
import logging

import Adafruit_PCA9685
import numpy as np
import picamera.array
from keras.models import load_model


def init_cam():
    cam = picamera.PiCamera(resolution=(250, 70), framerate=60)
    cam_output = picamera.array.PiRGBArray(cam, size=(250, 70))
    stream = cam.capture_continuous(cam_output, format='rgb',
                                    use_video_port=True)
    return cam, cam_output, stream


def command_from_pred(pred):
    command = {
        0: 300,
        1: 350,
        2: 400,
        3: 450,
        4: 500
    }
    power = command[np.argmax(pred)]
    return power


def control_car(cam_output, model_mlg, pict, pwm):
    pred = model_mlg.predict(np.array([pict.array]))
    logging.info(pred)
    power = command_from_pred(pred)
    pwm.set_pwm(2, 0, power)
    pwm.set_pwm(1, 0, 420)
    cam_output.truncate(0)


def stop_car(pwm):
    pwm.set_pwm(1, 0, 400)
    pwm.set_pwm(2, 0, 400)


def run(cam, cam_output, model_mlg, pwm, stream):
    cam.start_preview()
    for pict in stream:
        try:
            control_car(cam_output, model_mlg, pict, pwm)
        except:
            stop_car(pwm)
            raise


def main():
    # Objects Initialisation
    # Camera
    cam, cam_output, stream = init_cam()

    # Model
    model_mlg = load_model('/home/pi/ironcar/autopilots/my_autopilot_big.hdf5')

    # Arduino
    pwm = Adafruit_PCA9685.PCA9685()

    run(cam, cam_output, model_mlg, pwm, stream)


if __name__ == '__main__':
    main()
