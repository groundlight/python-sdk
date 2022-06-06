# User Guide

## Pre-reqs

For all the examples, there are 3 pre-reqs:

1. Install with `pip` or `poetry`.

    ```Bash
    # pip
    $ pip install groundlight

    # poetry
    $ poetry add groundlight
    ```

1. To access the API, you need an API token. You can create one in the [groundlight app](https://app.positronix.ai/reef/my-account/api-tokens). Then, add it as an environment variable called `GROUNDLIGHT_API_TOKEN`:

    ```Bash
    $ export GROUNDLIGHT_API_TOKEN=tok_abc123
    ```

1. Create the `Groundlight` API client. We usually use `gl` as a shorthand name, but you are free to name it what you like!
   
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

In practice, you may want to check for a new result on your query. For example, after a cloud reviewer labels your query. For example, you can use the `image_query.id` after the above `submit_image_query()` call.

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

### Handling HTTP errors

If there is an HTTP error during an API call, it will raise an `ApiException`. You can access different metadata from that exception:

```Python
from groundlight import ApiException, Groundlight

gl = Groundlight()
try:
    detectors = gl.list_detectors()
except ApiException as e:
    print(e)
    print(e.args)
    print(e.body)
    print(e.headers)
    print(e.reason)
    print(e.status)
```
