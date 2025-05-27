# DetectorGroup


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [readonly] 
**name** | **str** |  | 

## Example

```python
from groundlight_openapi_client.models.detector_group import DetectorGroup

# TODO update the JSON string below
json = "{}"
# create an instance of DetectorGroup from a JSON string
detector_group_instance = DetectorGroup.from_json(json)
# print the JSON string representation of the object
print DetectorGroup.to_json()

# convert the object into a dict
detector_group_dict = detector_group_instance.to_dict()
# create an instance of DetectorGroup from a dict
detector_group_from_dict = DetectorGroup.from_dict(detector_group_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


