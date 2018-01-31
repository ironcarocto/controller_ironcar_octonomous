import datetime
import json
import os

from python.ironcar_master import commands_json_file


def init_folder():
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

    return save_folder


def load_commands():
    with open(commands_json_file) as json_file:
        return json.load(json_file)