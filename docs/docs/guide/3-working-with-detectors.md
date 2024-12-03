# Working with Detectors

### Explicitly create a new detector

Typically you'll use the `get_or_create_detector(name: str, query: str)` method to find an existing detector you've already created with the same name, or create a new one if it doesn't exists. But if you'd like to force creating a new detector you can also use the `create_detector(name: str, query: str)` method

<!-- Don't test because we don't allow reusing the same name across multiple detectors -->

```python notest
from groundlight import Groundlight

gl = Groundlight()

# highlight-start
detector = gl.create_detector(name="your_detector_name", query="is there a hummingbird near the feeder?")
# highlight-end
```

### Retrieve an existing detector
To work with a detector that you've previously created, you need to retrieve it using its unique identifier. This is typical in Groundlight applications where you want to continue to use a detector you've already created.

<!-- Don't test because the ID can't be faked -->

```python notest
from groundlight import Groundlight

gl = Groundlight()

# highlight-start
detector = gl.get_detector(id="your_detector_id")
# highlight-end
```

Alternatively, you can retrieve a detector by its name:

```python notest
from groundlight import Groundlight

gl = Groundlight()

# highlight-start
detector = gl.get_detector_by_name(name="your_detector_name")
# highlight-end
```

### List your detectors
To manage and interact with your detectors, you might need to list them. Groundlight provides a straightforward way to retrieve a list of detectors you've created. By default, the list is paginated to show 10 results per page, but you can customize this to suit your needs.

```python
from groundlight import Groundlight

gl = Groundlight()

# highlight-start
# Defaults to 10 results per page
detectors = gl.list_detectors()

# Pagination: 1st page of 5 results per page
detectors = gl.list_detectors(page=1, page_size=5)
# highlight-end
```

### [BETA] Create a Counting Detector
So far, all of the detectors we've created have been binary classification detectors. But what if you want to count the number of objects in an image? You can create a counting detector to do just that. Counting detectors also return bounding boxes around the objects they count.

:::note

Counting Detectors are available on [Pro, Business, and Enterprise plans](https://www.groundlight.ai/pricing).

:::

```python notest
from groundlight import ExperimentalApi

gl_experimental = ExperimentalApi()

# highlight-start
detector = gl_experimental.create_counting_detector(name="your_detector_name", query="How many cars are in the parking lot?", max_count=20)
# highlight-end
```

### [BETA] Create a Multi-Class Detector
If you want to classify images into multiple categories, you can create a multi-class detector.

```python notest
from groundlight import ExperimentalApi

gl_experimental = ExperimentalApi()

# highlight-start
class_names = ["Golden Retriever", "Labrador Retriever", "German Shepherd"]
detector = gl_experimental.create_multiclass_detector(
    name, query="What kind of dog is this?", class_names=class_names
)
# highlight-end
```