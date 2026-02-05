# DetectorGroupRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 

## Example

```python
from groundlight_openapi_client.models.detector_group_request import DetectorGroupRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DetectorGroupRequest from a JSON string
detector_group_request_instance = DetectorGroupRequest.from_json(json)
# print the JSON string representation of the object
print(DetectorGroupRequest.to_json())

# convert the object into a dict
detector_group_request_dict = detector_group_request_instance.to_dict()
# create an instance of DetectorGroupRequest from a dict
detector_group_request_from_dict = DetectorGroupRequest.from_dict(detector_group_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


