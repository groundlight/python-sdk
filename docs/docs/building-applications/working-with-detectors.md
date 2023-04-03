---
sidebar_position: 3
---

# Working with Detectors

### Explicitly create a new detector

Typically you'll use the `get_or_create_detector(name: str, query: str)` method to find an existing detector you've already created with the same name, or create a new one if it doesn't exists. But if you'd like to force creating a new detector you can also use the `create_detector(name: str, query: str)` method

```python
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

### Retrieve an image query

In practice, you may want to check for a new result on your query. For example, after a cloud reviewer labels your query. For example, you can use the `image_query.id` after the above `submit_image_query()` call.

<!-- Don't test because the ID can't be faked -->

```python notest
from groundlight import Groundlight

gl = Groundlight()
# highlight-start
image_query = gl.get_image_query(id="iq_YOUR_IMAGE_QUERY_ID")
# highlight-end
```

### List your previous image queries

```python
from groundlight import Groundlight

gl = Groundlight()
# highlight-start
# Defaults to 10 results per page
image_queries = gl.list_image_queries()

# Pagination: 1st page of 5 results per page
image_queries = gl.list_image_queries(page=1, page_size=5)
# highlight-end
```

### Adding labels to existing image queries

Groundlight lets you start using models by making queries against your very first image, but there are a few situations where you might either have an existing dataset, or you'd like to handle the escalation response programatically in your own code but still include the label to get better responses in the future. With your `image_query` from either `submit_image_query()` or `get_image_query()` you can add the label directly. Note that if the query is already in the escalation queue due to low ML confidence or audit thresholds, it may also receive labels from another source.

```python
from groundlight import Groundlight
from PIL import Image
import requests

gl = Groundlight()
d = gl.get_or_create_detector(name="doorway", query="Is the doorway open?")
image = Image.open(
    requests.get("https://images.selfstorage.com/large-compress/2174925f24362c479b2.jpg", stream=True).raw
)
image_query = gl.submit_image_query(detector=d, image=image)
# highlight-start
image_query.add_label(image_query, 'YES'). # or 'NO'
# highlight-end
```

The only valid labels at this time are `'YES'` and `'NO'`
