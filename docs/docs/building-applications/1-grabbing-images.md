# Grabbing Images

Groundlight's SDK accepts images in many popular formats.

## PIL

The Groundlight SDK can accept PIL images directly in `submit_image_query`.  Here's an example:

```python
from PIL import Image

gl = Groundlight()
det = gl.get_or_create_detector(name="path-clear", query="Is the path clear?")
pil_img = Image.open("./docs/static/img/doorway.jpg")
gl.submit_image_query(detector, pil_img)
```

## OpenCV

OpenCV is a popular image processing library, with many utilities for working with images.
OpenCV images are stored as numpy arrays.  (Note they are stored in BGR order, not RGB order, but as of Groundlight SDK v0.8 this is the expected order.)
OpenCV's images can be send directly to `submit_image_query` as follows:

```python notest
import cv2

cam = cv2.VideoCapture(0)  # Initialize camera (0 is the default index)

_, frame = cam.read()  # Capture one frame
gl.submit_image_query(detector, frame)  # Send the frame to Groundlight
cap.release()  # Release the camera
```


## Numpy

The Groundlight SDK can accept images as `numpy` arrays. They should be in the standard HWN format in BGR color order, matching OpenCV standards.
Pixel values should be from 0-255 (not 0.0-1.0 as floats). So `uint8` data type is preferable since it saves memory.

Here's sample code to create an 800x600 random image in numpy:

```python notest
import numpy as np

np_img = np.random.uniform(low=0, high=255, size=(600, 800, 3)).astype(np.uint8)
gl.submit_image_query(detector, np_img)
```

### Channel order: BGR vs RGB

Groundlight expects images in BGR order, because this is standard for OpenCV, which uses numpy arrays as image storage.
Most other image libraries use RGB order, so you may need to reverse the channel order before sending to Groundlight.
If you have an RGB array, you must reverse the channel order before sending it to Groundlight, like:

```python notest
bgr_img = rgb_img[:, :, ::-1]
```

Note this change was made in v0.8 of the Groundlight SDK.  In previous versions, RGB order was expected.  
The difference can be surprisingly subtle when red and blue get swapped.  Often images just look a little off, but sometimes they look very wrong.

Here's an example of a subtle difference:
![Correct color order](/img/michonne.jpg)
![Swapped color channels](/img/michonne-bgr.jpg)

In industrial settings, the difference can be very subtle.
![Correct color order](/img/cnc-gripper.jpg)
![Swapped color channels](/img/cnc-gripper-bgr.jpg)


