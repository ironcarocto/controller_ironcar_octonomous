import os

import numpy as np
import imageio


class Memory:
    def __init__(self, n_img=0, save_folder="."):
        self.save_folder = save_folder
        self.n_img = n_img

    def save(self, img, curr_gas, curr_direction):
        image_name = (
            'frame_{0}_gas_{1}_dir_{2}_.jpg'
            .format(str(self.n_img),
                    str(curr_gas),
                    str(curr_direction)))
        image_path = os.path.join(self.save_folder, image_name)
        img_arr = np.array(img, copy=True)
        imageio.imwrite(image_path, img_arr)
        self.n_img += 1


class Forget:
    def save(self, img, curr_gas, curr_direction):
        pass
