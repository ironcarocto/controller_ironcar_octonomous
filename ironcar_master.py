from threading import Thread

from socketIO_client import SocketIO

# *********************************** Parameters ******************************
from ironcar.connection import Car
from ironcar.setup import init_folder
from ironcar.state import State

models_path = './autopilots/'

fps = 60

cam_resolution = (250, 150)

commands_json_file = "_commands.json"

file_count = 0

# *****************************************************************************

# --------------------------- SETUP ------------------------


save_folder = init_folder()

car = Car()
socketIO = SocketIO('http://localhost', port=8000, wait_for_connection=False)

state = State("started", "training", True, car, save_folder, cam_resolution, socketIO, models_path)

# --------------- Starting server and threads ----------------
mode_function = state.default_call

socketIO.emit('msg2user', 'Starting Camera thread')
camera_thread = Thread(target=state.camera_loop, args=())
camera_thread.start()

socketIO.emit('msg2user', 'Camera thread started! Please select a mode.')
socketIO.on('mode_update', state.on_switch_mode)
socketIO.on('model_update', state.on_model_selected)
socketIO.on('starterUpdate', state.on_start)
socketIO.on('maxSpeedUpdate', state.on_max_speed_update)
socketIO.on('gas', state.on_gas)
socketIO.on('dir', state.on_dir)

try:
    socketIO.wait()
except KeyboardInterrupt:
    running = False
    camera_thread.join()
