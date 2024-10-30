# Groundlight Python SDK

Groundlight makes it simple to build reliable visual applications. Read the [full documentation here](https://code.groundlight.ai/python-sdk/).

## Computer Vision powered by Natural Language

```bash
pip install groundlight
```

Build a working computer vision system in just a few lines of python:

```python
from groundlight import Groundlight

gl = Groundlight()
det = gl.get_or_create_detector(name="doorway", query="Is the doorway open?")
img = "./docs/static/img/doorway.jpg"  # Image can be a file or a Python object
image_query = gl.submit_image_query(detector=det, image=img)
print(f"The answer is {image_query.result}")
```

### How does it work?

Your images are first analyzed by machine learning (ML) models which are automatically trained on your data. If those models have high enough confidence, that's your answer. But if the models are unsure, then the images are progressively escalated to more resource-intensive analysis methods up to real-time human review. So what you get is a computer vision system that starts working right away without even needing to first gather and label a dataset. At first it will operate with high latency, because people need to review the image queries. But over time, the ML systems will learn and improve so queries come back faster with higher confidence.

## Learn more

Some more resources you might like:

- [Code Documentation](https://code.groundlight.ai/python-sdk/docs/getting-started)
- [Python SDK on PyPi](https://pypi.org/project/groundlight/) or [GitHub](https://github.com/groundlight/python-sdk)
- [Company](https://www.groundlight.ai/)
- [Login to the Groundlight Dashboard](https://dashboard.groundlight.ai/)
