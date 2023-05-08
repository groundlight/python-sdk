# Numpy, PIL, OpenCV - using common libraries

## Smaller is better!

Groundlight is optimized to run on small edge devices. As such, you can use the Groundlight SDK without
installing large libraries like `numpy` or `OpenCV`.

But if you're already installing them, we'll use them. Our SDK detects if these libraries are installed
and will make use of them if they're present. If not, we'll gracefully degrade, and tell you what's
wrong if you try to use these features.

## Numpy

The Groundlight SDK can accept images as `numpy` arrays. They should be in the standard HWN format in BGR color order, matching OpenCV standards.
Pixel values should be from 0-255 (not 0.0-1.0 as floats). SO `uint8` data type is preferable since it saves memory.

Here's sample code to create an 800x600 random image in numpy:

```python notest
import numpy as np

img = np_img = np.random.uniform(0, 255, (600, 800, 3))
```

If you have an RGB array, you must reverse the channel order before sending it to Groundlight, like:

```python notest
bgr_img = rgb_img[:, :, ::-1]
```


## PIL

The Groundlight SDK can accept PIL images directly in `submit_image_query`.

## OpenCV

OpenCV creates images that are stored as numpy arrays. So can send them to `submit_image_query` directly.