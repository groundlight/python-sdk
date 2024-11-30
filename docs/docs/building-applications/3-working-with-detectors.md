# Working with Detectors

### Explicitly create a new detector

Typically you'll use the `get_or_create_detector(name: str, query: str)` method to find an existing detector you've already created with the same name, or create a new one if it doesn't exists. But if you'd like to force creating a new detector you can also use the `create_detector(name: str, query: str)` method

<!-- Don't test because we don't allow reusing the same name across multiple detectors -->

```python notest
from groundlight import Groundlight

gl = Groundlight()
# highlight-start
detector = gl.create_detector(name="your_detector_name", query="is this what we want to see?")
# highlight-end
```

### Retrieve an existing detector

<!-- Don't test because the ID can't be faked -->

```python notest
from groundlight import Groundlight

gl = Groundlight()
# highlight-start
detector = gl.get_detector(id="YOUR_DETECTOR_ID")
# highlight-end
```

### List your detectors

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