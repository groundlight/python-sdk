# Groundlight Python SDK

Check out our [full documentation here](https://groundlight.github.io/python-sdk/)!

## Computer vision made simple

How to build a working computer vision system in just 5 lines of python code:

```shell
$ pip install groundlight
```

```python
from groundlight import Groundlight

gl = Groundlight()
d = gl.get_or_create_detector(name="door", query="Is the door open?")  # define with natural language
image_query = gl.submit_image_query(detector=d, image=jpeg_img)  # send in an image
print(f"The answer is {image_query.result}")  # get the result
```

Groundlight makes it simple to understand images. You can easily create computer vision detectors
just by describing what you want to know using natural language. Groundlight uses a combination of
advanced AI and real-time human monitors to automatically turn your images and queries into a
customized machine learning (ML) model for your application.
