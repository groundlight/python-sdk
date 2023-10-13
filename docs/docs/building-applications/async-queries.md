# Asynchronous Queries

Groundlight provides a simple interface for submitting asynchronous queries. This is useful for times in which the thread or machine submitting image queries is not the same thread or machine that will be retrieving and using the results. For example, you might have a forward deployed robot or camera that submits image queries to Groundlight, and a separate server that retrieves the results and takes action based on them. We will refer to these two machines as the **submitting machine** and the **retrieving machine**.

## Setup Submitting Machine
On the **submitting machine**, you will need to install the Groundlight Python SDK. Then you can submit image queries asynchronously using the `ask_async` interface (read the full documentation [here](TODO put link here)). `ask_async` submits your query and returns as soon as the query is submitted. It does not wait for an answer to be available prior to returning to minimize the time your program spends interacting with Groundlight. As a result, the `ImageQuery` object `ask_async` returns lacks a `result` (the `result` field will `None`). This is alright for this use case as the **submitting machine** is not interested in the result. Instead the **submitting machine** just needs to communicate the `ImageQuery.id`s to the **retrieving machine** - this might be done via a database, a message queue, or some other mechanism. For this example, we assume you are using a database where you save the `ImageQuery.id` to it via `db.save(image_query.id)`.

```python notest
from groundlight import Groundlight
import cv2
from time import sleep

detector = gl.get_or_create_detector(name="your_detector_name", query="your_query")

cam = cv2.VideoCapture(0)  # Initialize camera (0 is the default index) 

while True:  # TODO: add a way to exit this loop... not sure what makes sense here
    _, image = cam.read()  # Capture one frame from the camera
    image_query = gl.ask_async(detector=detector, image=image)  # Submit the frame to Groundlight
    db.save(image_query.id)  # Save the image_query.id to a database for the retrieving machine to use
    sleep(10) # Sleep for 10 seconds before submitting the next query

cam.release()  # Release the camera

```

## Setup Retrieving Machine
On the **retrieving machine** you will need to install the Groundlight Python SDK. Then you can retrieve the results of the image queries submitted by another machine using `get_image_query`. The **retrieving machine** can then use the `ImageQuery.result` to take action based on the result for whatever application you are building. For this example, we assume your application looks up the next image query to process from a database via `db.get_next_image_query_id()`.
```python notest
from groundlight import Groundlight

detector = gl.get_or_create_detector(name="your_detector_name", query="your_query")

def process_image_query(image_query_id):
    '''
    : param image_query_id: the id of the image query to process from the database
    '''
    
    # retrieve the image query from Groundlight
    image_query = gl.get_image_query(id=image_query_id)
    result = image_query.result
    # take action based on the result 
    if result == 'YES':
        # take action if the result is YES
        pass
    elif result == 'NO':
        # take action if the result is NO
        pass
    elif result ==  'UNCLEAR'
        # take action if the result is UNCLEAR
        pass

while True:  # TODO: add a way to exit this loop... not sure what makes sense here
    image_query_id = db.get_next_image_query_id()  # get the next image query id from the database
    process_image_query(image_query_id)  # process the image query 
```

## Important Considerations
When you submit an image query asynchronously, ML prediction on your query is not instant. So attempting to retrieve the result immediately after submitting the query will likely result in an 'UNCLEAR' result as Groundlight is still processing your query. Instead, if your code needs a `result` synchronously we recommend using one of our methods with a polling mechanism to retrieve the result, like `submit_image_query`. 

```python notest
from groundlight import Groundlight
from PIL import Image

detector = gl.get_or_create_detector(name="your_detector_name", query="your_query")
image = Image.open("/path/to/your/image.jpg")
image_query = gl.ask_async(detector=detector, image=image)  # Submit the frame to Groundlight
result = image_query.result  # This will likely be 'UNCLEAR' as Groundlight is still processing your query
```

# TODO: what other considerations are there?


