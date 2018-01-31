from threading import Thread

from socketIO_client import SocketIO

from conf import models_path, fps, cam_resolution, save_folder
from ironcar.camera import Camera
from ironcar.car import Car
from ironcar.car_control import CarControl
from ironcar.driving_model import DrivingModel
from ironcar.driving_modes import AllDrivingModes
from ironcar.logger import Logger
from ironcar.memory import Memory
from ironcar.pilot import Pilot


def env_setup():
    # ---- Inputs ----
    socket = SocketIO('http://localhost', port=8000,
                      wait_for_connection=False)
    camera = Camera(cam_resolution, fps)

    # ---- Outputs ----
    memory = Memory(save_folder=save_folder)
    logger = Logger()

    # ---- Car ----
    car_control = CarControl()
    car = Car(state="started", car_control=car_control, logger=logger)

    # ---- Pilot ----
    driving_model = DrivingModel(models_path, logger=logger)
    driving_modes = AllDrivingModes(intruction_stream=socket,
                                    car=car,
                                    driving_model=driving_model,
                                    memory=memory)
    pilot = Pilot(car=car,
                  visual_input=camera,
                  driving_modes=driving_modes,
                  message_stream=socket)
    return pilot, car, socket


def define_event_handlers(pilot, car, socket):
    # Pilot events
    socket.on('mode_update', pilot.switch_mode)
    socket.on('model_update', pilot.load_model)
    # Car events
    socket.on('starterUpdate', car.start_or_stop)
    socket.on('gas', car.set_gas)
    socket.on('dir', car.set_direction)
    socket.on('maxSpeedUpdate', car.set_max_speed)


def main():
    pilot, car, socket = env_setup()
    define_event_handlers(pilot, car, socket)

    socket.emit('msg2user', 'Starting Camera thread')
    driving_thread = Thread(target=pilot.drive_loop, args=())
    driving_thread.start()
    socket.emit('msg2user', 'Camera thread started! Please select a mode.')

    try:
        socket.wait()
    except KeyboardInterrupt:
        pilot.stop_driving()
        driving_thread.join()


if __name__ == '__main__':
    main()
