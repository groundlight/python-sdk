# Binary Classification Detectors

Binary classification detectors are used to answer yes/no questions about images. Most of Groundlight's documentation examples are for binary classification detectors, as they are the simplest type of detector.

In order to create a binary classification detector, you need to provide a query that asks a yes/no question. For example, "Is there an eagle visible?" or "Is the door fully closed?".

```python notest
from groundlight import Groundlight
gl = Groundlight()

# highlight-start
detector = gl.create_detector(
    name="eagle-detector",
    query="Is there an eagle visible?",
    confidence_threshold=0.9,
)
# highlight-end
```

## Submit an Image Query to a Binary Classification Detector

Now that you have created a binary classification detector, you can submit an image query to it.

```python notest
from groundlight import Groundlight
gl = Groundlight()

detector = gl.get_detector_by_name("eagle-detector")

# highlight-start
# Check if an eagle is visible in an image
image_query = gl.submit_image_query(detector, "path/to/image.jpg")
# highlight-end

print(f"Result: {image_query.result.label}")
print(f"Confidence: {image_query.result.confidence}")
```

Binary classification detectors return a `label` attribute in the result object, which will be either `"YES"` or `"NO"`. If a query is ambiguous, it is also possible for the detector to return an `"UNCLEAR"` label.

The `confidence` attribute represents the confidence level in the predicted label, which (for a binary classification detector) is a value between 0.5 and 1. A higher confidence score indicates that the model is more certain about its prediction.

## Add a label to a Binary Classification Detector

To provide ground truth labels for binary classification detectors, you can specify the label as either `"YES"`, `"NO"`, or `"UNCLEAR"`. This helps improve the accuracy of your detector over time.

```python notest
from groundlight import Groundlight
gl = Groundlight()

# highlight-start
# Add a binary label to the image query from the previous example
gl.add_label(image_query, label="YES")
# highlight-end
```
