from threading import Thread

from socketIO_client import SocketIO

# *********************************** Parameters ******************************
from python.ironcar.camera import Camera
from python.ironcar.car import Car
from python.ironcar.car_control import CarControl
from python.ironcar.conf import init_folder
from python.ironcar.driving_model import DrivingModel
from python.ironcar.driving_modes import AllDrivingModes
from python.ironcar.logger import Logger
from python.ironcar.memory import Memory
from python.ironcar.pilot import Pilot

# --------------------------- SETUP ------------------------

# ---- Conf ----
models_path = './autopilots/'
fps = 60
cam_resolution = (256, 160)
commands_json_file = "_commands.json"
file_count = 0
save_folder = init_folder()

# ---- Inputs ----
socketIO = SocketIO('http://localhost', port=8000, wait_for_connection=False)
camera = Camera(cam_resolution, fps)

# ---- Outputs ----
memory = Memory(save_folder=save_folder)
logger = Logger()

# ---- Car ----
car_control = CarControl()
car = Car("started", True, car_control=car_control, logger=logger)

# ---- Control ----
driving_model = DrivingModel(models_path, logger=logger)
driving_modes = AllDrivingModes(intruction_stream=socketIO,
                                car=car,
                                driving_model=driving_model,
                                memory=memory)
pilot = Pilot(car=car,
              visual_input=camera,
              driving_modes=driving_modes,
              message_stream=SocketIO)

# --------------- Starting server and threads ----------------
socketIO.emit('msg2user', 'Starting Camera thread')
camera_thread = Thread(target=pilot.drive_loop, args=())
camera_thread.start()

socketIO.emit('msg2user', 'Camera thread started! Please select a mode.')

# Pilot events
socketIO.on('mode_update', pilot.switch_mode)
socketIO.on('model_update', pilot.load_model)

# Car events
socketIO.on('starterUpdate', car.start_or_stop)
socketIO.on('gas', car.set_gas)
socketIO.on('dir', car.set_direction)
socketIO.on('maxSpeedUpdate', car.set_max_speed)

try:
    socketIO.wait()
except KeyboardInterrupt:
    car.running = False
    camera_thread.join()
