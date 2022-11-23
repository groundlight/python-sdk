# Groundlight Python SDK

Groundlight makes it simple to understand images.  You can easily create computer vision detectors just by describing what you want to know using natural language.

## Computer vision made simple

How to build a working computer vision system in just 5 lines of python code:

```Python
from groundlight import Groundlight
gl = Groundlight()
d = gl.get_or_create_detector(name="door", query="Is the door open?")  # define with natural language
image_query = gl.submit_image_query(detector=d, image=jpeg_img)  # send in an image
print(f"The answer is {image_query.result}")  # get the result
```

**How does it work?**  Your images are first analyzed by machine learning (ML) models which are automatically trained on your data.  If those models have high enough confidence, that's your answer.  But if the models are unsure, then the images are progressively escalated to more resource-intensive analysis methods up to real-time human review.  So what you get is a computer vision system that starts working right away without even needing to first gather and label a dataset.  At first it will operate with high latency, because people need to review the image queries.  But over time, the ML systems will learn and improve so queries come back faster with higher confidence.

*Note: The SDK is currently in "beta" phase.  Interfaces are subject to change in future versions.*


## Managing confidence levels and latency

Groundlight gives you a simple way to control the trade-off of latency against accuracy.  The longer you can wait for an answer to your image query, the better accuracy you can get.  In particular, if the ML models are unsure of the best response, they will escalate the image query to more intensive analysis with more complex models and real-time human monitors as needed.  Your code can easily wait for this delayed response.  Either way, these new results are automatically trained into your models so your next queries will get better results faster.

The desired confidence level is set as the escalation threshold on your detector.  This determines what is the minimum confidence score for the ML system to provide before the image query is escalated.

For example, say you want to set your desired confidence level to 0.95, but that you're willing to wait up to 60 seconds to get a confident response.  

```Python
d = gl.get_or_create_detector(name="trash", query="Is the trash can full?", confidence=0.95)
image_query = gl.submit_image_query(detector=d, image=jpeg_img, wait=60)
# This will wait until either 30 seconds have passed or the confidence reaches 0.95
print(f"The answer is {image_query.result}")
```

Or if you want to run as fast as possible, set `wait=0`.  This way you will only get the ML results, without waiting for escalation.  Image queries which are below the desired confidence level still be escalated for further analysis, and the results are incorporated as training data to improve your ML model, but your code will not wait for that to happen.

```Python
image_query = gl.submit_image_query(detector=d, image=jpeg_img, wait=0)
```

If the returned result was generated from an ML model, you can see the confidence score returned for the image query:

```Python
print(f"The confidence is {image_query.result.confidence}")
```

## Getting Started

1. Install the `groundlight` SDK.  Requires python version 3.7 or higher.  See [prerequisites](#Prerequisites).

    ```Bash
    $ pip3 install groundlight
    ```

1. To access the API, you need an API token. You can create one on the
   [groundlight web app](https://app.groundlight.ai/reef/my-account/api-tokens).

The API token should be stored securely.  You can use it directly in your code to initialize the SDK like:

```python
gl = Groundlight(api_token="<YOUR_API_TOKEN>")
```

which is an easy way to get started, but is NOT a best practice.  Please do not commit your API Token to version control!  Instead we recommend setting the `GROUNDLIGHT_API_TOKEN` environment variable outside your code so that the SDK can find it automatically.

```bash
$ export GROUNDLIGHT_API_TOKEN=api_2GdXMflhJi6L_example
$ python3 glapp.py
```



## Prerequisites

### Using Groundlight SDK on Ubuntu 18.04

Ubuntu 18.04 still uses python 3.6 by default, which is end-of-life.  We recommend setting up python 3.8 as follows:

```
# Prepare Ubuntu to install things
sudo apt-get update
# Install the basics
sudo apt-get install -y python3.8 python3.8-distutils curl
# Configure `python3` to run python3.8 by default
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 10
# Download and install pip3.8
curl https://bootstrap.pypa.io/get-pip.py > /tmp/get-pip.py
sudo python3.8 /tmp/get-pip.py
# Configure `pip3` to run pip3.8
sudo update-alternatives --install /usr/bin/pip3 pip3 $(which pip3.8) 10
# Now we can install Groundlight!
pip3 install groundlight
```

## Using Groundlight on the edge

Starting your model evaluations at the edge reduces latency, cost, network bandwidth, and energy. Once you have downloaded and installed your Groundlight edge models, you can configure the Groundlight SDK to use your edge environment by configuring the 'endpoint' to point at your local environment as such:

```Python
from groundlight import Groundlight
gl = Groundlight(endpoint="http://localhost:6717")
```

(Edge model download is not yet generally available.)

## Advanced

### Explicitly create a new detector

Typically you'll use the ```get_or_create_detector(name: str, query: str)``` method to find an existing detector you've already created with the same name, or create a new one if it doesn't exists.  But if you'd like to force creating a new detector you can also use the ```create_detector(name: str, query: str)``` method

```Python
detector = gl.create_detector(name="your_detector_name", query="is this what we want to see?")
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

### Adding labels to existing image queries

Groundlight lets you start using models by making queries against your very first image, but there are a few situations where you might either have an existing dataset, or you'd like to handle the escalation response programatically in your own code but still include the label to get better responses in the future.  With your ```image_query``` from either ```submit_image_query()``` or ```get_image_query()``` you can add the label directly.  Note that if the query is already in the escalation queue due to low ML confidence or audit thresholds, it may also receive labels from another source.

```Python
add_label(image_query, 'YES').   # or 'NO'
```

The only valid labels at this time are ```'YES'``` and ```'NO'```


### Handling HTTP errors

If there is an HTTP error during an API call, it will raise an `ApiException`. You can access different metadata from that exception:

```Python
from groundlight import ApiException, Groundlight

gl = Groundlight()
try:
    detectors = gl.list_detectors()
except ApiException as e:
    # Many fields available to describe the error
    print(e)
    print(e.args)
    print(e.body)
    print(e.headers)
    print(e.reason)
    print(e.status)
```

