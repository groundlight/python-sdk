# GetDetectorMetrics200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**summary** | [**GetDetectorMetrics200ResponseSummary**](GetDetectorMetrics200ResponseSummary.md) |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.get_detector_metrics200_response import GetDetectorMetrics200Response

# TODO update the JSON string below
json = "{}"
# create an instance of GetDetectorMetrics200Response from a JSON string
get_detector_metrics200_response_instance = GetDetectorMetrics200Response.from_json(json)
# print the JSON string representation of the object
print GetDetectorMetrics200Response.to_json()

# convert the object into a dict
get_detector_metrics200_response_dict = get_detector_metrics200_response_instance.to_dict()
# create an instance of GetDetectorMetrics200Response from a dict
get_detector_metrics200_response_from_dict = GetDetectorMetrics200Response.from_dict(get_detector_metrics200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


