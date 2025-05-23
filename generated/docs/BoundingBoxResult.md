# BoundingBoxResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**confidence** | **float** |  | [optional] 
**source** | **str** |  | [optional] 
**result_type** | **str** |  | [optional] 
**from_edge** | **bool** |  | [optional] 
**label** | **str** |  | 

## Example

```python
from groundlight_openapi_client.models.bounding_box_result import BoundingBoxResult

# TODO update the JSON string below
json = "{}"
# create an instance of BoundingBoxResult from a JSON string
bounding_box_result_instance = BoundingBoxResult.from_json(json)
# print the JSON string representation of the object
print(BoundingBoxResult.to_json())

# convert the object into a dict
bounding_box_result_dict = bounding_box_result_instance.to_dict()
# create an instance of BoundingBoxResult from a dict
bounding_box_result_from_dict = BoundingBoxResult.from_dict(bounding_box_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


