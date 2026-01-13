# Bounding Box Detectors

Bounding box detectors are used to detect and localize objects in an image by returning bounding boxes around each detected object.

```python notest
from groundlight import ExperimentalApi
gl = ExperimentalApi()

# highlight-start
detector = gl.create_bounding_box_detector(
    name="dog-detector",
    query="Draw a bounding box around each dog in the image",
    class_name="dog",
    max_num_bboxes=25,
    confidence_threshold=0.6,
)
# highlight-end
```

Bounding box detectors should be provided with a query that asks the model to identify and localize objects in an image, such as "Draw a bounding box around each dog in the image".

The `class_name` parameter specifies the type of object to detect, and this label will be assigned to each returned bounding box.

The `max_num_bboxes` parameter sets the maximum number of bounding boxes that the detector will return (default: 10). If there are more objects in the image than the maximum, the result label will be `GREATER_THAN_MAX`.

The `confidence_threshold` parameter sets the minimum confidence level required for the ML model's predictions. If the model's confidence falls below this threshold, the query will be sent for human review.

:::note
Bounding Box Detectors are currently in beta and available through the `ExperimentalApi`. They are available on [Business and Enterprise plans](https://www.groundlight.ai/pricing).
:::

## Submit an Image Query to a Bounding Box Detector

Now that you have created a bounding box detector, you can submit an image query to it.

```python notest
from groundlight import ExperimentalApi
gl = ExperimentalApi()

detector = gl.get_detector_by_name("dog-detector")

# highlight-start
# Detect dogs in an image
image_query = gl.submit_image_query(detector, "path/to/image.jpg")
# highlight-end

print(f"Label: {image_query.result.label}")
print(f"Confidence: {image_query.result.confidence}")
print(f"Bounding Boxes: {image_query.rois}")
```

For bounding box detectors, the `label` attribute of the result object will be one of:
- `NO_OBJECTS`: No objects of the specified class were detected in the image
- `BOUNDING_BOX`: Objects were detected and bounding boxes are available in `image_query.rois`
- `GREATER_THAN_MAX`: More objects were detected than the `max_num_bboxes` limit
- `UNCLEAR`: The result was unclear

The `rois` (regions of interest) attribute contains the list of bounding boxes, each with:
- `geometry`: Bounding box coordinates (`left`, `top`, `right`, `bottom`) as values between 0 and 1
- `label`: The class name of the detected object
- `score`: Confidence score for this specific object

<!-- TODO: display an example image with bounding boxes -->

:::tip Drawing Bounding Boxes
You can visualize the bounding boxes returned by bounding box detectors using a library like OpenCV. Here's an example of how to draw bounding boxes on an image:

```python notest
import cv2
import numpy as np

def draw_bounding_boxes(image_path, rois):
    """
    Draw bounding boxes on an image based on ROIs returned from a bounding box detector.

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

## Add a Label to a Bounding Box Detector

The Groundlight API allows you to add labels to image queries, including Region of Interest (ROI) data.
When adding a label to a bounding box detector, you must include the ROIs that correspond to the objects in the image.

```python notest
from groundlight import ExperimentalApi
gl = ExperimentalApi()

# highlight-start
# Add a bounding box label with corresponding ROIs to the image query from the previous example.
#   ROIs are specified as (left, top) and (right, bottom) coordinates, with values
#   between 0 and 1 representing the percentage of the image width and height.
roi1 = gl.create_roi("dog", (0.1, 0.2), (0.3, 0.4))
roi2 = gl.create_roi("dog", (0.5, 0.3), (0.7, 0.6))
rois = [roi1, roi2]
gl.add_label(image_query, label="BOUNDING_BOX", rois=rois)
# highlight-end
```

Valid label values for bounding box detectors are:
- `"NO_OBJECTS"`: Use when there are no objects of the target class in the image (no ROIs needed)
- `"BOUNDING_BOX"`: Use when objects are present and you are providing ROIs
- `"GREATER_THAN_MAX"`: Use when there are more objects than `max_num_bboxes`
- `"UNCLEAR"`: Use when the image is unclear or the answer cannot be determined
