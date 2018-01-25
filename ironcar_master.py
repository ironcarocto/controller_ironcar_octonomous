from threading import Thread

from socketIO_client import SocketIO

# *********************************** Parameters ******************************
from ironcar.camera import Camera
from ironcar.connection import CarControl
from ironcar.setup import init_folder
from ironcar.car import Car

models_path = './autopilots/'

fps = 60

cam_resolution = (250, 150)

commands_json_file = "_commands.json"

file_count = 0

# *****************************************************************************

# --------------------------- SETUP ------------------------


save_folder = init_folder()

car_control = CarControl()
socketIO = SocketIO('http://localhost', port=8000, wait_for_connection=False)
camera = Camera(cam_resolution, fps)

car = Car("started", "training", True, car_control, save_folder, socketIO, models_path)

# --------------- Starting server and threads ----------------
mode_function = car.default_call

socketIO.emit('msg2user', 'Starting Camera thread')
camera_thread = Thread(target=car.drive_loop, args=())
camera_thread.start()

socketIO.emit('msg2user', 'Camera thread started! Please select a mode.')
socketIO.on('mode_update', car.on_switch_mode)
socketIO.on('model_update', car.on_model_selected)
socketIO.on('starterUpdate', car.on_start)
socketIO.on('maxSpeedUpdate', car.on_max_speed_update)
socketIO.on('gas', car.on_gas)
socketIO.on('dir', car.on_dir)

try:
    socketIO.wait()
except KeyboardInterrupt:
    running = False
    camera_thread.join()
