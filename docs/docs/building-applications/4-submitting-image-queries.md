# Submitting Image Queries
Once you have [created a `Detector`](./3-working-with-detectors.md) and [captured an image](./2-grabbing-images.md), you can submit your image to Groundlight for analysis.

## Submit an Image Query
The primary method for submitting an image query is `submit_image_query(detector: Detector, image: Any)`. This method takes a `Detector` object and an image as input and returns an `ImageQuery` object.
```python notest
from groundlight import Groundlight

gl = Groundlight()
detector = gl.get_detector(id="det_abcdef...")

# highlight-start
image_query = gl.submit_image_query(detector=detector, image="path/to/image.jpg")
# highlight-end
```

`submit_image_query` provides fine-grained control over how the `ImageQuery` is processed. For example, a per-query confidence threshold can be set (defaults to the `Detector`'s confidence threshold), and the query can be set to wait for up to a certain amount of time for a confident response (defaults to 30s). For example:
```python notest
from groundlight import Groundlight

gl = Groundlight()
detector = gl.get_detector(id="det_abcdef...")

# highlight-start
image_query = gl.submit_image_query(
    detector=detector,
    image="path/to/image.jpg",
    confidence_threshold=0.95,
    wait=10.0,  # seconds
)
# highlight-end
```

See the [API Reference](../api-reference/api-reference.md)
) for more information on the `submit_image_query` method.

## Aliases for `submit_image_query`
For convenience, the `submit_image_query` method has aliases for the different patterns of usage. These aliases are `ask_confident`, `ask_ml`, and `ask_async`.

### Get the first confident answer
`ask_confident` evaluates an image with Groundlight waiting until an answer above the confidence threshold
        of the detector is reached or the wait period has passed.
```python notest
from groundlight import Groundlight

gl = Groundlight()
detector = gl.get_detector(id="det_abcdef...")

# highlight-start
image_query = gl.ask_confident(detector=detector, image="path/to/image.jpg")
# highlight-end
```

### Get the first available answer, regardless of confidence
`ask_ml` evaluates an image with Groundlight and returns the first answer Groundlight can provide, agnostic of confidence. There is no wait period when using this method. It is called `ask_ml` because our machine learning models are earliest on our escalation ladder and thus always the fastest to respond.
```python notest
from groundlight import Groundlight

gl = Groundlight()
detector = gl.get_detector(id="det_abcdef...")

# highlight-start
image_query = gl.ask_ml(detector=detector, image="path/to/image.jpg")
# highlight-end
```

### Submit an ImageQuery asynchronously
`ask_async` is a convenience method for submitting an `ImageQuery` asynchronously. This is equivalent to calling `submit_image_query` with `want_async=True` and `wait=0`. Use `get_image_query` to retrieve the `result` of the ImageQuery.

```python notest
from groundlight import Groundlight

gl = Groundlight()
detector = gl.get_detector(id="det_abcdef...")

# highlight-start
# Submit ImageQuery asynchronously
image_query = gl.ask_async(detector=detector, image="path/to/image.jpg")

# Do other work while waiting for the result
sleep(1.0)

# Retrieve the result of the ImageQuery. Note that the provided
# result can change over time - as the query is escalated through
# our ladder - until a confident answer is reached.
image_query = gl.get_image_query(id=image_query.id)
# highlight-end
```

See this [guide](./7-async-queries.md) for more information on ImageQueries submitted asynchronously.

## Working with Image Queries Post-Submission

### Retrieve an Image Query

In practice, you may want to check for a new result on your query. For example, after a cloud reviewer labels your query. For example, you can use the `image_query.id` after the above `submit_image_query()` call.

<!-- Don't test because the ID can't be faked -->

```python notest
from groundlight import Groundlight

gl = Groundlight()
# highlight-start
image_query = gl.get_image_query(id="iq_YOUR_IMAGE_QUERY_ID")
# highlight-end
```

### List your previous Image Queries

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

### Add a label to an Image Query

Groundlight lets you start using models by making queries against your very first image, but there are a few situations where you might either have an existing dataset, or you'd like to handle the escalation response programatically in your own code but still include the label to get better responses in the future. With your `image_query` from either `submit_image_query()` or `get_image_query()` you can add the label directly. Note that if the query is already in the escalation queue due to low ML confidence or audit thresholds, it may also receive labels from another source.

```python
from groundlight import Groundlight
from PIL import Image
import requests

gl = Groundlight()
d = gl.get_or_create_detector(name="doorway", query="Is the doorway open?")
image_url= "https://images.selfstorage.com/large-compress/2174925f24362c479b2.jpg"
image = Image.open(requests.get(image_url, stream=True).raw)
image_query = gl.submit_image_query(detector=d, image=image)
# highlight-start
gl.add_label(image_query, 'YES') # or 'NO'
# highlight-end
```
