# BoundingBoxModeConfiguration


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**class_name** | **str** |  | 
**max_num_bboxes** | **int** |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.bounding_box_mode_configuration import BoundingBoxModeConfiguration

# TODO update the JSON string below
json = "{}"
# create an instance of BoundingBoxModeConfiguration from a JSON string
bounding_box_mode_configuration_instance = BoundingBoxModeConfiguration.from_json(json)
# print the JSON string representation of the object
print BoundingBoxModeConfiguration.to_json()

# convert the object into a dict
bounding_box_mode_configuration_dict = bounding_box_mode_configuration_instance.to_dict()
# create an instance of BoundingBoxModeConfiguration from a dict
bounding_box_mode_configuration_from_dict = BoundingBoxModeConfiguration.from_dict(bounding_box_mode_configuration_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


