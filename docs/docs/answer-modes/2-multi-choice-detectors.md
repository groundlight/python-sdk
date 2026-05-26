# Multiple Choice (Choose One) Detectors

If you want to classify images into one of several mutually exclusive categories, you can create a multi-class detector. As the "Choose One" name implies, the detector picks a single label from your list of `class_names` for each image.

```python notest
from groundlight import ExperimentalApi
gl_exp = ExperimentalApi()

# highlight-start
class_names = ["Golden Retriever", "Labrador Retriever", "German Shepherd", "Other"]
detector = gl_exp.create_multiclass_detector(
    name="dog-breed-detector",
    query="What kind of dog is this?",
    class_names=class_names,
)
# highlight-end
```

:::caution Use non-overlapping classes
Multi-class detectors work best when your classes are **mutually exclusive** — every image should belong to exactly one class. They are *not* multi-label detectors and will not return more than one label per image.

If an image could legitimately match more than one of your classes at the same time (for example, "Has a person" and "Has a vehicle" in the same frame), a multi-class detector is the wrong tool. Instead, create a separate [binary detector](1-binary-detectors.md) for each class so each one can fire independently.

A good rule of thumb: if you can rephrase your query as "Which **one** of these is it?" a multi-class detector is a great fit. If the natural phrasing is "Which of these are present?", reach for multiple binary detectors instead.
:::

:::tip
We recommend adding an "Other" class to your multi-class detector to handle cases where the image does not belong to any of the pre-defined classes.
:::

:::note
Multi-Class Detectors are available on [Business and Enterprise plans](https://www.groundlight.ai/pricing).
:::

## Submit an Image Query to a Multi-Class Detector

Now that you have created a multi-class detector, you can submit an image query to it.

```python notest
from groundlight import ExperimentalApi
gl_exp = ExperimentalApi()

detector = gl_exp.get_detector_by_name("dog-breed-detector")

# highlight-start
# Classify the breed of a dog in an image
image_query = gl_exp.submit_image_query(detector, "path/to/image.jpg")
# highlight-end

print(f"Result: {image_query.result.label}")
print(f"Confidence: {image_query.result.confidence}")
```

Multi-class detectors return a `label` attribute in the result object, which contains the predicted class label. The `label` attribute will be one of the class names provided when creating the detector. The `confidence` attribute represents the confidence level in the predicted class, which is a value between `1/len(class_names)` and 1.

## Add a label to a Multi-Class Detector

To provide ground truth labels for multi-class detectors, you can specify the label of the correct class.

```python notest
from groundlight import ExperimentalApi
gl_exp = ExperimentalApi()

# highlight-start
# Add a multi-class label to the image query from the previous example
gl_exp.add_label(image_query, label="German Shepherd")
# highlight-end
```
