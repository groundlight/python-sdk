# Setting Confidence Thresholds

## Introduction to Confidence Thresholds
When creating a Detector or submitting an ImageQuery, you can set the necessary confidence level for your use case. We call this the `confidence_threshold`. Tuning this value allows you to balance the trade-offs between accuracy and latency / cost.

Confidence scores represent the model's internal assessment of its prediction reliability. Groundlight models provide *calibrated* confidence scores, which means that, when a model makes a prediction with a confidence of 0.95, we expect that (under typical conditions) 95% of the time that prediction will be correct. In other words, a prediction with a confidence of 0.95 is expected to be correct 19 out of 20 times.

Confidence thresholds represent a minimum confidence that must be achieved for Groundlight to return an answer. If a confidence above the confidence threshold is not achieved, Groundlight will escalate your query up our heirarchy to stronger models and human reviewers. Confidence thresholds should be determined based on your application's acceptable error rate and the potential impact of those errors.

Higher confidence thresholds result in predictions that are more accurate but may take longer to process (because they are escalated to more complex/expensive models or human review). Lower confidence thresholds result in faster responses but may be less accurate. Over time, and as more human-provided labels are collected, the ML models will improve, and our fastest models will be able to provide higher confidence predictions more quickly.

## Configuring Timeouts

In some cases, challenging queries that require human review can take a number of seconds, so we provide both client-side and server-side timeouts to ensure that your application can continue to function even if the query takes longer than expected.

Set a client-side timeout by configuring the `wait` parameter in the `submit_image_query` method. This simply stops the client from waiting for a response after a certain amount of time.

Set a server-side timeout by configuring the `patience_time` parameter in the `submit_image_query` method. This tells Groundlight to deprioritize the query after a certain amount of time, which can be useful if the result of a query becomes less relevant over time. For example, if you are monitoring a live video feed, you may want to deprioritize queries that are more than a few seconds old so that our human reviewers can focus on the most recent data.

<!-- We skip tests here because the tests may be slow -->

```python notest
from groundlight import Groundlight
from PIL import Image
import requests

gl = Groundlight()
image_url = "https://www.photos-public-domain.com/wp-content/uploads/2010/11/over_flowing_garbage_can.jpg"
image = Image.open(requests.get(image_url, stream=True).raw)


d = gl.get_or_create_detector(
    name="trash",
    query="Is the trash can full?",
# highlight-start
    confidence_threshold=0.95,  # Set the confidence threshold to 0.95
# highlight-end
)

# This will wait until either 60 seconds have passed or the confidence reaches 0.95
image_query = gl.submit_image_query(
    detector=d,
    image=image,
# highlight-start
    wait=10,  # tell the client to stop waiting after 10 seconds
    patience_time=20,  # tell Groundlight to deprioritize the query after 20 seconds
# highlight-end
)

print(f"The answer is {image_query.result.label}")
print(f"The confidence is {image_query.result.confidence}")
```

:::tip

Tuning confidence_threshold lets you balance accuracy against latency.

Higher confidence levels lead to greater accuracy but typically result in increased latency. Additionally, achieving higher confidence necessitates more labels, which can raise labor costs.

Over time, our models will improve and become more confident, allowing you to achieve higher confidence levels more quickly while also reducing costs.

:::

## When Quick Answers are Needed

To execute an image query as fast as possible and get the first available answer regardless of confidence, use the `ask_ml` method (equivalent to setting `wait=0`). This method returns the first answer Groundlight can provide without waiting for the query to reach a specific confidence level.

```python notest continuation
image_query = gl.ask_ml(detector=d, image=image)
```

When using this method, low-confidence Image Queries will still be escalated to human review - this allows our models to continue to improve over time.