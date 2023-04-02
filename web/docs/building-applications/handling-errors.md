# Handling HTTP errors

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
