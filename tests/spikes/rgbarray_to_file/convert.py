from PIL import Image

import numpy as np

img_filename = "ironcar.jpg"
img = Image.open(img_filename)
img = img.convert("RGB")
rgb_array = np.array(img)
image_png = Image.fromarray(rgb_array, "RGB")

#alpha.show()
image_png.save('ironcar.png')