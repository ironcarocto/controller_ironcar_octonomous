import numpy as np


class Logger:
    def __init__(self, pred_dir="predictions_log", img_dir="images_logs"):
        self.img_dir = img_dir
        self.pred_dir = pred_dir
        self.file_count = 0

    def log_prediction(self, pred):
        print('pred : ', pred)
        path = '{}/prediction{}'.format(self.pred_dir, self.file_count)
        np.save(path, pred)
        self.file_count += 1

    def log_image(self, img):
        path = '{}/img{}'.format(self.img_dir, self.file_count)
        np.save(path, img)