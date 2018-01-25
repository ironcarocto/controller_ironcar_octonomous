import numpy as np
import picamera


class Camera(object):
    def __init__(self, cam_resolution, fps):
        cam = picamera.PiCamera(framerate=fps)
        cam.resolution = cam_resolution
        cam_output = picamera.array.PiRGBArray(cam, size=self.cam_resolution)
        self.cam_output = cam_output
        self.stream = cam.capture_continuous(cam_output,
                                             format="rgb",
                                             use_video_port=True)

    def picture_stream(self, file_count):
        for f in self.stream:
            img_arr = f.array
            np.save('images_log/img{}'.format(file_count), img_arr)
            yield img_arr
            self.cam_output.truncate(0)
