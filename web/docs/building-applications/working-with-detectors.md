---
sidebar_position: 3
---

# Working with Detectors

### Explicitly create a new detector

Typically you'll use the `get_or_create_detector(name: str, query: str)` method to find an existing detector you've already created with the same name, or create a new one if it doesn't exists. But if you'd like to force creating a new detector you can also use the `create_detector(name: str, query: str)` method

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

Groundlight lets you start using models by making queries against your very first image, but there are a few situations where you might either have an existing dataset, or you'd like to handle the escalation response programatically in your own code but still include the label to get better responses in the future. With your `image_query` from either `submit_image_query()` or `get_image_query()` you can add the label directly. Note that if the query is already in the escalation queue due to low ML confidence or audit thresholds, it may also receive labels from another source.

```Python
add_label(image_query, 'YES').   # or 'NO'
```

The only valid labels at this time are `'YES'` and `'NO'`
