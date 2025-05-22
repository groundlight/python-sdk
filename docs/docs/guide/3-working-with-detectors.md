# Working with Detectors

This guide will walk you through creating, retrieving, and managing detectors in Groundlight. Groundlight supports several detector modalities to suit different computer vision tasks - for more information on these modes, see the [Detector Answer Modes](../answer-modes/answer-modes.md) guide.


## Explicitly create a new detector

Typically you'll use the `get_or_create_detector(name: str, query: str)` method to find an existing detector you've already created with the same name, or create a new one if it doesn't exists. But if you'd like to force creating a new detector you can also use the `create_detector(name: str, query: str)` method

<!-- Don't test because we don't allow reusing the same name across multiple detectors -->

```python notest
from groundlight import Groundlight

gl = Groundlight()

# highlight-start
detector = gl.create_detector(name="your_detector_name", query="is there a hummingbird near the feeder?")
# highlight-end
```

## Retrieve an existing detector
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

## List your detectors
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
