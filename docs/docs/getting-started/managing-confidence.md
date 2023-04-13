# Confidence Levels

Groundlight gives you a simple way to control the trade-off of latency against accuracy. The longer you can wait for an answer to your image query, the better accuracy you can get. In particular, if the ML models are unsure of the best response, they will escalate the image query to more intensive analysis with more complex models and real-time human monitors as needed. Your code can easily wait for this delayed response. Either way, these new results are automatically trained into your models so your next queries will get better results faster.

The desired confidence level is set as the escalation threshold on your detector. This determines what is the minimum confidence score for the ML system to provide before the image query is escalated.

For example, say you want to set your desired confidence level to 0.95, but that you're willing to wait up to 60 seconds to get a confident response.

<!-- We skip tests here because the tests are too slow -->

```python notest
from groundlight import Groundlight
from PIL import Image
import requests

gl = Groundlight()
image = Image.open(
    requests.get("https://www.photos-public-domain.com/wp-content/uploads/2010/11/over_flowing_garbage_can.jpg", stream=True).raw
)

# highlight-start
d = gl.get_or_create_detector(name="trash", query="Is the trash can full?", confidence=0.95)

# This will wait until either 60 seconds have passed or the confidence reaches 0.95
image_query = gl.submit_image_query(detector=d, image=image, wait=60)
# highlight-end

print(f"The answer is {image_query.result}")
```

:::tip

Tuning confidence lets you balance accuracy against latency.
Higher confidence will get higher accuracy, but will generally require longer latency.

:::

Or if you want to run as fast as possible, set `wait=0`. This way you will only get the ML results, without waiting for escalation. Image queries which are below the desired confidence level still be escalated for further analysis, and the results are incorporated as training data to improve your ML model, but your code will not wait for that to happen.

```python notest continuation
image_query = gl.submit_image_query(detector=d, image=image, wait=0)
```

If the returned result was generated from an ML model, you can see the confidence score returned for the image query:

```python notest continuation
print(f"The confidence is {image_query.result.confidence}")
```
