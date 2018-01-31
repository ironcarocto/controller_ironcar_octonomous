import time

from python.ironcar.car import Car


class Pilot(object):
    def __init__(self, car: Car, visual_input,
                 driving_modes, message_stream, start_driving=True):
        self.car = car
        self.message_stream = message_stream
        self.driving_modes = driving_modes
        self.current_pilot_mode = self.driving_modes.get("rest")
        self.visual_input = visual_input
        self.is_driving = start_driving

    def stop_driving(self):
        self.is_driving = False

    # ------------------- Main loop  ---------------------
    # This function is launched on a separate thread that is supposed to run
    # permanently to get camera pics
    def drive_loop(self):
        for img_arr in self.visual_input.picture_stream():
            if not self.is_driving:
                break
            self.drive_from_image(img_arr)

    def drive_from_image(self, img):
        self.current_pilot_mode.drive(img)

    def load_model(self, model_name):
        try:
            self.car.stop()
            time.sleep(0.5)
            new_model_path = self.current_pilot_mode.load_model(model_name)
        except OSError:
            self.message_stream.emit('msg2user',
                                     'Failed loading model. '
                                     'Please select another one.')
        else:
            self.message_stream.emit('msg2user',
                                     'Loaded model at path : ' + str(
                                         new_model_path))

    def switch_mode(self, data):
        # always switch the starter to stopped when switching mode
        self.car.stop()
        self.message_stream.emit('starter')

        # Stop the gas before switching mode
        self.current_pilot_mode = self.driving_modes.get(data)

        # Make sure we stop even if the previous
        # mode sent a last command before switching.
        self.car.stop()