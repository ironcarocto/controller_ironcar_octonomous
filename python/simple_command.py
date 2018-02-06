#Import
from keras.models import load_model
import Adafruit_PCA9685
import picamera
import picamera.array
import numpy as np

#Objects Initialisation
###Camera
cam = picamera.PiCamera(resolution=(250,70), framerate=60)
cam_output = picamera.array.PiRGBArray(cam,size=(250,70))
stream = cam.capture_continuous(cam_output, format ='rgb', use_video_port = True)

###Model
model_mlg = load_model('/home/pi/ironcar/autopilots/my_autopilot_big.hdf5')

###Arduino
pwm = Adafruit_PCA9685.PCA9685()

command = {
        0 : 300, 
        1 : 350, 
        2 : 400, 
        3 : 450, 
        4 : 500
        }


cam.start_preview()

for pict in stream:
    pred = model_mlg.predict(np.array([pict.array]))
    print(pred)
    power = command[np.argmax(pred)]
    pwm.set_pwm(2,0, power)
    pwm.set_pwm(1,0,420)
    cam_output.truncate(0)

