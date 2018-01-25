import os

import numpy as np
import scipy.misc
import tensorflow as tf
from keras.models import load_model


class Car(object):
    def __init__(self, state, mode, running, car_control, save_folder,
                 socket, models_path, camera,
                 curr_direction=0, curr_gas=0, model=None, max_speed_rate=0.5):
        self.state = state
        self.mode = mode
        self.running = running
        self.n_img = 0
        self.file_count = 0
        self.save_folder = save_folder
        self.camera = camera

        self.car_control = car_control
        self.curr_direction = curr_direction
        self.curr_gas = curr_gas
        self.max_speed_rate = max_speed_rate

        self.model = None
        self.models_path = models_path
        self.current_model = model
        self.graph = None
        self.model_loaded = False if self.current_model is None else True

        self.socket = socket
        self.mode_function = self.default_call

    def get_gas_from_direction(self, dir):
        return 0.2

    # -------------------------- Driving Strategies ---------------------
    def default_call(self, img):
        pass

    def autopilot(self, img):
        img = np.array([img[80:, :, :]])
        with self.graph.as_default():
            pred = self.model.predict(img)
            print('pred : ', pred)
            np.save('predictions_log/prediction{}'.format(self.file_count),
                    pred)
            self.file_count += 1
            prediction = list(pred[0])
        index_class = prediction.index(max(prediction))

        local_dir = -1 + 2 * float(index_class) / float(len(prediction) - 1)
        local_gas = self.get_gas_from_direction(
            self.curr_direction) * self.max_speed_rate

        self.car_control.set_direction(local_dir)
        if self.state == "started":
            self.car_control.set_speed(local_gas)
        else:
            self.car_control.stop()

    def dirauto(self, img):
        img = np.array([img[80:, :, :]])
        with self.graph.as_default():
            pred = self.model.predict(img)
            print('pred : ', pred)

            prediction = list(pred[0])
        index_class = prediction.index(max(prediction))

        local_dir = -1 + 2 * float(index_class) / float(len(prediction) - 1)
        self.car_control.set_direction(local_dir)

    def training(self, img):
        image_name = os.path.join(self.save_folder,
                                  'frame_' + str(self.n_img) + '_gas_' +
                                  str(self.curr_gas) + '_dir_' + str(
                                      self.curr_direction) +
                                  '_' + '.jpg')
        img_arr = np.array(img[80:, :, :], copy=True)
        scipy.misc.imsave(image_name, img_arr)
        self.n_img += 1

    # ------------------- Main camera loop  ---------------------
    # This function is launched on a separate thread that is supposed to run
    # permanently to get camera pics
    def drive_loop(self):
        for img_arr in self.camera.picture_stream():
            if not self.running:
                break
            self.mode_function(img_arr)

    # ------------------ SocketIO callbacks-----------------------
    def on_model_selected(self, model_name):
        if model_name == self.current_model or model_name == -1: return 0
        new_model_path = self.models_path + model_name
        self.socket.emit('msg2user',
                         'Loading model at path : ' + str(new_model_path))
        try:
            self.model = load_model(new_model_path)
            self.graph = tf.get_default_graph()
            self.current_model = model_name
            self.socket.emit('msg2user', ' Model Loaded!')
            self.model_loaded = True
            self.on_switch_mode(self.mode)
        except OSError:
            self.socket.emit('msg2user',
                             ' Failed loading model. Please select another one.')

    def on_switch_mode(self, data):
        # always switch the starter to stopped when switching mode
        if self.state == "started":
            self.state = "stopped"
            self.socket.emit('starter')
        # Stop the gas before switching mode
        self.car_control.stop()
        self.mode = data
        if data == "dirauto":
            self.socket.off('dir')
            if self.model_loaded:
                self.mode_function = self.dirauto
                self.socket.emit('msg2user',
                                 ' Direction auto mode. Please control the gas using a keyboard or a gamepad.')
            else:
                print("model not loaded")
                self.socket.emit('msg2user', ' Please load a model first')
        elif data == "auto":
            self.socket.off('gas')
            self.socket.off('dir')
            if self.model_loaded:
                self.mode_function = self.autopilot
                self.socket.emit('msg2user',
                                 ' Autopilot mode. Use the start/stop button to free the gas command.')
            else:
                print("model not loaded")
                self.socket.emit('msg2user', 'Please load a model first')
        elif data == "training":
            self.socket.on('gas', self.on_gas)
            self.socket.on('dir', self.on_dir)
            self.mode_function = self.training
            self.socket.emit('msg2user',
                             ' Training mode. Please use a keyboard or a gamepad for control.')
        else:
            self.mode_function = self.default_call
            self.socket.emit('msg2user', ' Resting')
        print('switched to mode : ', data)
        # Make sure we stop even if the previous mode sent a last command before switching.
        self.car_control.stop()

    def on_start(self, data):
        self.state = data
        print('starter set to  ' + data)

    def on_dir(self, data):
        self.curr_direction = float(data)
        if self.curr_direction == 0:
            self.car_control.straight_dir()
        else:
            self.car_control.set_direction(self.curr_direction)

    def on_gas(self, data):
        self.curr_gas = float(data) * self.max_speed_rate
        print('THIS IS THE CURRENT GAS_COMMAND ', self.curr_gas)
        if self.curr_gas < 0:
            self.car_control.brake()
        elif self.curr_gas == 0:
            self.car_control.stop()
        else:
            self.car_control.set_speed(self.curr_gas)

    def on_max_speed_update(self, new_max_speed):
        self.max_speed_rate = new_max_speed
