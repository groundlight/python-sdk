# Examples

## Pre-reqs

For all the examples, there are 2 pre-reqs:

1. To access the API, you need an API token. You can create one at [app.groundlight.ai](https://app.positronix.ai/reef/my-account/api-tokens). Then, add it as an environment variable called `GROUNDLIGHT_API_TOKEN`:

    ```Bash
    $ export GROUNDLIGHT_API_TOKEN=tok_abc123
    ```

1. Create the `Groundlight` API client. We usually use `gl` as a shorthand name, but your are free to name it what you like!
   
    ```Python
    from groundlight import Groundlight
    gl = Groundlight()
    ```
## Basics

#### Create a new detector

```Python
detector = gl.create_detector(name="Dog", query="Is it a dog?")
```

#### Retrieve a detector

```Python
detector = gl.get_detector(id="YOUR_DETECTOR_ID")
```

#### List your detectors

```Python
# Defaults to 10 results per page
detectors = gl.list_detectors()

# Pagination: 3rd page of 25 results per page
detectors = gl.list_detectors(page=3, page_size=25)
```

#### Submit an image query

```Python
image_query = gl.submit_image_query(detector_id="YOUR_DETECTOR_ID", image="path/to/filename.jpeg")
```

#### Retrieve an image query

In practice, you may want to check for a new result on your query. For example, after a cloud reviewer labels your query.

```Python
image_query = gl.get_image_query(id="YOUR_IMAGE_QUERY_ID")
```

#### List your previous image queries

```Python
# Defaults to 10 results per page
image_queries = gl.list_image_queries()

# Pagination: 3rd page of 25 results per page
image_queries = gl.list_image_queries(page=3, page_size=25)
```

## Advanced

#### Use a different API endpoint

```Python
from groundlight import Groundlight

# Integ
integ_gl = Groundlight(endpoint="https://device.integ.positronix.ai/device-api")

# Local
local_gl = Groundlight(endpoint="http://localhost:8000/device-api")
```

#### Do more with the object models

You can see the different model types [here](generated/model.py). (TODO: Use something like [autodoc_pydantic](https://github.com/mansenfranzen/autodoc_pydantic) to create docs).

All of the `Groundlight` methods return [pydantic](https://pydantic-docs.helpmanual.io/) models - `Detector`, `ImageQuery`, `PaginatedDetectorList`, etc. This provides several benefits: you can access model fields with dot notation, get auto-complete in your IDE, have `model.dict()`, `model.json()`, `model.pickle()` serializers, etc. See more on the [pydantic docs](https://pydantic-docs.helpmanual.io/usage/models/).
