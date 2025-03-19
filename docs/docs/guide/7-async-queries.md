# Using Asynchronous Queries

Groundlight provides a simple interface for submitting asynchronous queries. This is useful for situations in which the thread or process or machine submitting image queries is not the same thread or machine that will be retrieving and using the results.

For example, you might have a forward deployed robot or camera that submits image queries to Groundlight, and a separate server that retrieves the results and takes action based on them. We will refer to these two machines as the **submitting machine** and the **retrieving machine**.

## Setup Submitting Machine
On the **submitting machine**, you will need to install the Groundlight Python SDK. Then you can submit image queries asynchronously using the `ask_async` interface (read the full documentation [here](pathname:///python-sdk/api-reference-docs/#groundlight.client.Groundlight.ask_async)).

`ask_async` submits your query and immediately returns, without waiting for an answer. This minimizes the time your program spends interacting with Groundlight. Consequently, the `ImageQuery` object returned by `ask_async` does not contain a `result` (the `result` field will be `None`). This is suitable for scenarios where the **submitting machine** does not need the result. Instead, the **submitting machine** only needs to share the `ImageQuery.id` with the **retrieving machine**. This can be done through a database, message queue, or another method. In this example, we assume you are using a database to save the `ImageQuery.id` with `db.save(image_query.id)`.

```python notest
from time import sleep
from framegrab import FrameGrabber
from groundlight import Groundlight

# Create a FrameGrabber for a generic USB camera (e.g., a webcam)
config = {'input_type': 'generic_usb'}
grabber = FrameGrabber.create_grabber(config)

detector = gl.get_or_create_detector(name="your_detector_name", query="your_query")

while True:
    image = grabber.grab()

    # highlight-start
    image_query = gl.ask_async(detector=detector, image=image)
    db.save(image_query.id)  # Save the image_query.id to a database for the retrieving machine to use
    # highlight-end

    sleep(10) # Sleep for 10 seconds before grabbing the next image

grabber.release()
```

## Setup Retrieving Machine
On the **retrieving machine**, ensure the Groundlight Python SDK is installed. You can then use the `get_image_query` method to fetch results of image queries submitted by the **submitting machine**. The **retrieving machine** can utilize the `ImageQuery.result` to perform actions based on the application's requirements. In this example, we assume your application retrieves the next image query ID to process from a database using `db.get_next_image_query_id()`. This function should return `None` when all `ImageQuery` entries have been processed.

```python notest
from groundlight import Groundlight

detector = gl.get_or_create_detector(name="your_detector_name", query="your_query")

image_query_id = db.get_next_image_query_id()

while image_query_id is not None:
    # highlight-start
    image_query = gl.get_image_query(id=image_query_id)  # retrieve the image query from Groundlight
    # highlight-end
    result = image_query.result

    # take action based on the result of the image query
    if result.label == 'YES':
        pass # TODO: do something based on your application
    elif result.label == 'NO':
        pass # TODO: do something based on your application
    elif result.label == 'UNCLEAR':
        pass # TODO: do something based on your application

    # update image_query_id for next iteration of the loop
    image_query_id = db.get_next_image_query_id()
```

## Important Considerations
When you submit an image query asynchronously, ML prediction on your query is **not** instant. So attempting to retrieve the result immediately after submitting an async query will likely result in an `UNCLEAR` result as Groundlight is still processing your query. Instead, if your code needs a `result` synchronously we recommend using one of our methods with a polling mechanism to retrieve the result (e.g. `ask_confident`). You can see all of the interfaces available in the documentation [here](pathname:///python-sdk/api-reference-docs/#groundlight.client.Groundlight).

```python notest
from PIL import Image
from groundlight import Groundlight

detector = gl.get_or_create_detector(name="your_detector_name", query="your_query")
image = Image.open("/path/to/your/image.jpg")

image_query = gl.ask_async(detector=detector, image=image)  # Submit async query to Groundlight
assert image_query.result is None  # IQs returned from `ask_async` will not have a result

image_query = gl.get_image_query(id=image_query.id)  # Immediately retrieve the image query from Groundlight
result = image_query.result  # This may be 'UNCLEAR' as Groundlight continues to process the query

image_query = gl.wait_for_confident_result(id=image_query.id)  # Poll for a confident result from Groundlight
result = image_query.result
```