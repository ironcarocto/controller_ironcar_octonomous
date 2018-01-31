import os

import numpy as np
import tensorflow as tf
from keras.models import load_model


class DrivingModel(object):
    def __init__(self, models_path, logger, model=None, graph=None):
        self.models_path = models_path
        self.logger = logger
        self.model = model
        self.model_loaded = False if self.model is None else True
        self.graph = graph

    def decide_direction_and_gas(self, img, curr_direction):
        img = np.array([img[80:, :, :]])
        with self.graph.as_default():
            pred = self.model.predict(img)

        self.logger.log_prediction(pred)

        prediction = list(pred[0])
        index_class = prediction.index(max(prediction))
        local_dir = -1 + 2 * float(index_class) / float(len(prediction) - 1)
        local_gas = self.get_gas_from_direction(curr_direction)
        return local_dir, local_gas

    def get_gas_from_direction(self, direction):
        return 0.2

    def load_model(self, model_name):
        new_model_path = os.path.join(self.models_path, model_name)
        self.model = load_model(new_model_path)
        self.graph = tf.get_default_graph()
        self.model_loaded = True
        return new_model_path
