import datetime
import json
import os
from threading import Thread

import Adafruit_PCA9685
import numpy as np
import picamera
import picamera.array
import scipy.misc
import tensorflow as tf
from keras.models import load_model
from socketIO_client import SocketIO

# *********************************** Parameters ************************************
models_path = './autopilots/'

fps = 60

cam_resolution = (250, 150)

commands_json_file = "commands.json"

file_count = 0

# ***********************************************************************************

# --------------------------- SETUP ------------------------

ct = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
save_folder = os.path.join('datasets/', str(ct))
image_logs = 'images_logs'
predictions_logs = 'predictions_logs'

if not os.path.exists(image_logs):
    os.makedirs(image_logs)

if not os.path.exists(predictions_logs):
    os.makedirs(predictions_logs)

if not os.path.exists(save_folder):
    os.makedirs(save_folder)

with open(commands_json_file) as json_file:
    commands = json.load(json_file)

# PWM setup
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)

state, mode, running = "stop", "training", True
n_img = 0
curr_dir, curr_gas = 0, 0
current_model = None
max_speed_rate = 0.5
model_loaded = False


# --------------- Set helper functions --------------

def set_speed(gas):
    global pwm
    pwm.set_pwm(commands['gas'], 0, int(
        gas * (commands['drive_max'] - commands['neutral']) + commands[
            'neutral']))


def set_direction(direction):
    global pwm
    pwm.set_pwm(commands['direction'], 0, int(
        direction * (commands['right'] - commands['left']) / 2. + commands[
            'straight']))


def stop_car():
    global pwm
    pwm.set_pwm(commands['gas'], 0, commands['neutral'])


def brake_car():
    global pwm
    pwm.set_pwm(commands['gas'], 0, commands['stop'])


def straight_dir():
    global pwm
    pwm.set_pwm(commands['direction'], 0, commands['straight'])


# ---------------- Different modes functions ----------------


def get_gas_from_dir(dir):
    return 0.2


def default_call(img):
    pass


def autopilot(img):
    global model, graph, state, max_speed_rate, file_count

    img = np.array([img[80:, :, :]])
    with graph.as_default():
        pred = model.predict(img)
        print('pred : ', pred)
        np.save('predictions_log/prediction{}'.format(file_count), pred)
        file_count += 1
        prediction = list(pred[0])
    index_class = prediction.index(max(prediction))

    local_dir = -1 + 2 * float(index_class) / float(len(prediction) - 1)
    local_gas = get_gas_from_dir(curr_dir) * (max_speed_rate)
    # local_gas = 0.00002#print(local_gas)

    set_direction(local_dir)
    if state == "started":
        set_speed(local_gas)
    else:
        stop_car()


def dirauto(img):
    global model, graph, file_count

    img = np.array([img[80:, :, :]])
    with graph.as_default():
        pred = model.predict(img)
        print('pred : ', pred)

        prediction = list(pred[0])
    index_class = prediction.index(max(prediction))

    local_dir = -1 + 2 * float(index_class) / float(len(prediction) - 1)
    set_direction(local_dir)


def training(img):
    global n_img, curr_dir, curr_gas
    image_name = os.path.join(save_folder, 'frame_' + str(n_img) + '_gas_' +
                              str(curr_gas) + '_dir_' + str(curr_dir) +
                              '_' + '.jpg')
    img_arr = np.array(img[80:, :, :], copy=True)
    scipy.misc.imsave(image_name, img_arr)
    n_img += 1


# ------------------- Main camera loop  ---------------------
# This function is launched on a separate thread that is supposed to run permanently
# to get camera pics
def camera_loop():
    global state, mode_function, running, file_count

    cam = picamera.PiCamera(framerate=fps)
    cam.resolution = cam_resolution
    cam_output = picamera.array.PiRGBArray(cam, size=cam_resolution)
    stream = cam.capture_continuous(cam_output, format="rgb",
                                    use_video_port=True)

    for f in stream:
        img_arr = f.array
        np.save('images_log/img{}'.format(file_count), img_arr)
        if not running:
            break
        mode_function(img_arr)

        cam_output.truncate(0)


# ------------------ SocketIO callbacks-----------------------
# This will try to load a model when receiving a callback from the node server
def on_model_selected(model_name):
    global current_model, models_path, model_loaded, model, graph, mode
    if model_name == current_model or model_name == -1: return 0
    new_model_path = models_path + model_name
    socketIO.emit('msg2user', 'Loading model at path : ' + str(new_model_path))
    try:
        model = load_model(new_model_path)
        graph = tf.get_default_graph()
        current_model = model_name
        socketIO.emit('msg2user', ' Model Loaded!')
        model_loaded = True
        on_switch_mode(mode)
    except OSError:
        socketIO.emit('msg2user',
                      ' Failed loading model. Please select another one.')


def on_switch_mode(data):
    global mode, state, mode_function, model_loaded, model, graph
    # always switch the starter to stopped when switching mode
    if state == "started":
        state = "stopped"
        socketIO.emit('starter')
    # Stop the gas before switching mode
    stop_car()
    mode = data
    if data == "dirauto":
        socketIO.off('dir')
        if model_loaded:
            mode_function = dirauto
            socketIO.emit('msg2user',
                          ' Direction auto mode. Please control the gas using a keyboard or a gamepad.')
        else:
            print("model not loaded")
            socketIO.emit('msg2user', ' Please load a model first')
    elif data == "auto":
        socketIO.off('gas')
        socketIO.off('dir')
        if model_loaded:
            mode_function = autopilot
            socketIO.emit('msg2user',
                          ' Autopilot mode. Use the start/stop button to free the gas command.')
        else:
            print("model not loaded")
            socketIO.emit('msg2user', 'Please load a model first')
    elif data == "training":
        socketIO.on('gas', on_gas)
        socketIO.on('dir', on_dir)
        mode_function = training
        socketIO.emit('msg2user',
                      ' Training mode. Please use a keyboard or a gamepad for control.')
    else:
        mode_function = default_call
        socketIO.emit('msg2user', ' Resting')
    print('switched to mode : ', data)
    # Make sure we stop even if the previous mode sent a last command before switching.
    stop_car()


def on_start(data):
    global state
    state = data
    print('starter set to  ' + data)


def on_dir(data):
    global curr_dir
    curr_dir = float(data)
    if curr_dir == 0:
        # print(commands['straight'])
        straight_dir()
    else:
        # print(int(curr_dir * (commands['right'] - commands['left'])/2. + commands['straight']))
        set_direction(curr_dir)


def on_gas(data):
    global curr_gas, max_speed_rate
    curr_gas = float(data) * max_speed_rate
    print('THIS IS THE CURRENT GAS ', curr_gas)
    if curr_gas < 0:
        brake_car()
    elif curr_gas == 0:
        stop_car()
    else:
        #    print(curr_gas * (commands['drive_max'] - commands['drive']) + commands['neutral'])
        set_speed(curr_gas)


def on_max_speed_update(new_max_speed):
    global max_speed_rate
    max_speed_rate = new_max_speed


# --------------- Starting server and threads ----------------
mode_function = default_call
socketIO = SocketIO('http://localhost', port=8000, wait_for_connection=False)
socketIO.emit('msg2user', 'Starting Camera thread')
camera_thread = Thread(target=camera_loop, args=())
camera_thread.start()
socketIO.emit('msg2user', 'Camera thread started! Please select a mode.')
socketIO.on('mode_update', on_switch_mode)
socketIO.on('model_update', on_model_selected)
socketIO.on('starterUpdate', on_start)
socketIO.on('maxSpeedUpdate', on_max_speed_update)
socketIO.on('gas', on_gas)
socketIO.on('dir', on_dir)

try:
    socketIO.wait()
except KeyboardInterrupt:
    running = False
    camera_thread.join()
