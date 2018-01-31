import numpy as np


class Logger:
    def __init__(self):
        self.file_count = 0

    def log_prediction(self, pred):
        print('pred : ', pred)
        np.save('predictions_log/prediction{}'.format(self.file_count), pred)
        self.file_count += 1