# User Guide

`groundlight` is a python SDK for working with the Groundlight API. You can send image queries and receive predictions powered by a mixture of machine learning models and human labelers in-the-loop.

*Note: The SDK is currently in "alpha" phase.*

## Pre-reqs

1. Install the `groundlight` sdk.

    ```Bash
    $ pip install groundlight
    ```

1. To access the API, you need an API token. You can create one on the [groundlight website](https://app.positronix.ai/reef/my-account/api-tokens).

1. Use the `Groundlight` client!
   
    ```Python
    from groundlight import Groundlight
    gl = Groundlight(api_token="<YOUR_API_TOKEN>")
    ```

    The API token should be stored securely - do not commit it to version control! Alternatively, you can use the token by setting the `GROUNDLIGHT_API_TOKEN` environment variable.

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
