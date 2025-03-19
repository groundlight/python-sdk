# Count Detectors

Counting detectors are used to count the number of objects in an image. Groundlight's counting detectors also return bounding boxes around the objects they count.

```python notest
from groundlight import ExperimentalApi
gl_exp = ExperimentalApi()

# highlight-start
detector = gl_exp.create_counting_detector(
    name="car-counter",
    query="How many cars are in the parking lot?",
    class_name="car",
    max_count=20,
    confidence_threshold=0.2,
)
# highlight-end
```

Counting detectors should be provided with a query that asks "how many" objects are in the image.

A maximum count (of 25 or fewer) must be specified when creating a counting detector. This is the maximum number of objects that the detector will count in an image. Groundlight's ML models are optimized for counting up to 20 objects, but you can increase the maximum count to 25 if needed. If you have an application that requires counting more than 25 objects, please [contact us](mailto:support@groundlight.ai).

The `confidence_threshold` parameter sets the minimum confidence level required for the ML model's predictions. If the model's confidence falls below this threshold, the query will be sent for human review. Count detectors can have a `confidence_threshold` set to any value between `1/(max_count + 2)` and 1.

:::note
Counting Detectors are available on [Business and Enterprise plans](https://www.groundlight.ai/pricing).
:::

## Submit an Image Query to a Counting Detector

Now that you have created a counting detector, you can submit an image query to it.

```python notest
from groundlight import ExperimentalApi
gl_exp = ExperimentalApi()

detector = gl_exp.get_detector_by_name("car-counter")

# highlight-start
# Count the number of cars in an image
image_query = gl_exp.submit_image_query(detector, "path/to/image.jpg")
# highlight-end

print(f"Counted {image_query.result.count} cars")
print(f"Confidence: {image_query.result.confidence}")
print(f"Bounding Boxes: {image_query.rois}")
```

In the case of counting detectors, the `count` attribute of the result object will contain the number of objects counted in the image. The `confidence` attribute represents the confidence level in the specific count. Note that this implies that confidences may be lower (on average) for counting detectors with a higher maximum count.

<!-- TODO: display an example image with bounding boxes -->

:::tip Drawing Bounding Boxes
You can visualize the bounding boxes returned by counting detectors using a library like OpenCV. Here's an example of how to draw bounding boxes on an image:

```python notest
import cv2
import numpy as np

def draw_bounding_boxes(image_path, rois):
    """
    Draw bounding boxes on an image based on ROIs returned from a counting detector.

    Args:
        image_path: Path to the image file
        rois: List of ROI objects returned from image_query.rois
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image from {image_path}")
    height, width = image.shape[:2]

    # Draw bounding boxes
    for roi in rois:
        x1 = int(roi.geometry.left * width)
        y1 = int(roi.geometry.top * height)
        x2 = int(roi.geometry.right * width)
        y2 = int(roi.geometry.bottom * height)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label_text = f"{roi.label}: {roi.score:.2f}"
        cv2.putText(image, label_text, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the image
    cv2.imshow("Image with Bounding Boxes", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage:
# image_query = gl.submit_image_query(detector, "path/to/image.jpg")
# draw_bounding_boxes("path/to/image.jpg", image_query.rois)
```
:::

## Add a label to a Counting Detector

The Groundlight API allows you to add labels to image queries, including Region of Interest (ROI) data.
When adding a label to a counting detector, if you include ROIs, the number of ROIs should match
the count you are labeling.

```python notest
from groundlight import ExperimentalApi
gl_exp = ExperimentalApi()

# highlight-start
# Add a count label with corresponding ROIs to the image query from the previous example.
#   ROIs are specified as (left, top) and (right, bottom) coordinates, with values
#   between 0 and 1 representing the percentage of the image width and height.
roi1 = gl_exp.create_roi("car", (0.1, 0.2), (0.2, 0.3))
roi2 = gl_exp.create_roi("car", (0.4, 0.4), (0.5, 0.6))
roi3 = gl_exp.create_roi("car", (0.6, 0.5), (0.8, 0.9))
rois = [roi1, roi2, roi3]
gl_exp.add_label(image_query, label=len(rois), rois=rois)
# highlight-end
```