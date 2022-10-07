# Groundlight User Guide

Groundlight makes it simple to understand images.  You can send image queries and receive predictions powered by a mixture of advanced machine learning models backed up by real people.

*Note: The SDK is currently in "beta" phase.  Interfaces are subject to change.*

## Getting Started

1. Install the `groundlight` sdk.

    ```Bash
    $ pip install groundlight
    ```

1. To access the API, you need an API token. You can create one on the
   [groundlight web app](https://app.groundlight.ai/reef/my-account/api-tokens).

The API token should be stored securely.  Some of the code samples demonstrate including the API token in your source code, which is NOT a best practice.  Do not commit your API Token to version control!  Instead we recommend setting the `GROUNDLIGHT_API_TOKEN` environment variable.


## Basic Usage

How to build a simple computer vision system in 5 lines of python:

```Python
from groundlight import Groundlight
gl = Groundlight()

# Create a new detector: use natural language to describe what you want to understand
detector = gl.create_detector(name="door", query="Is the door open?")

# Send an image to the detector
image_query = gl.submit_image_query(detector=detector, image="path/to/filename.jpeg")

# Show the results
print(f"The answer is {image_query.result}")
```

## Using Groundlight on the edge

OFten it is impractical to send every image to the cloud for analysis.  Setting up a Groundlight edge environment can help you achieve lower latency and reduce costs.  Once you have downloaded and installed your edge model, configure your Groundlight SDK client to use the edge environment by configuring the `endpoint` as such:

    ```Python
    from groundlight import Groundlight
    gl = Groundlight(endpoint="http://localhost:5717")
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

### Retrieve an existing detector

```Python
detector = gl.get_detector(id="YOUR_DETECTOR_ID")
```

### List your detectors

```Python
# Defaults to 10 results per page
detectors = gl.list_detectors()

# Pagination: 3rd page of 25 results per page
detectors = gl.list_detectors(page=3, page_size=25)
```

### Submit an image query

```Python
image_query = gl.submit_image_query(detector_id="YOUR_DETECTOR_ID", image="path/to/filename.jpeg")
```

### Retrieve an image query

In practice, you may want to check for a new result on your query. For example, after a cloud reviewer labels your query. For example, you can use the `image_query.id` after the above `submit_image_query()` call.

```Python
image_query = gl.get_image_query(id="YOUR_IMAGE_QUERY_ID")
```

### List your previous image queries

```Python
# Defaults to 10 results per page
image_queries = gl.list_image_queries()

# Pagination: 3rd page of 25 results per page
image_queries = gl.list_image_queries(page=3, page_size=25)
```
