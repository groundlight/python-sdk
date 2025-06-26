# BBoxGeometry

Mixin for serializers to handle data in the StrictBaseModel format

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**left** | **float** |  | 
**top** | **float** |  | 
**right** | **float** |  | 
**bottom** | **float** |  | 
**x** | **float** |  | [readonly] 
**y** | **float** |  | [readonly] 

## Example

```python
from groundlight_openapi_client.models.b_box_geometry import BBoxGeometry

# TODO update the JSON string below
json = "{}"
# create an instance of BBoxGeometry from a JSON string
b_box_geometry_instance = BBoxGeometry.from_json(json)
# print the JSON string representation of the object
print BBoxGeometry.to_json()

# convert the object into a dict
b_box_geometry_dict = b_box_geometry_instance.to_dict()
# create an instance of BBoxGeometry from a dict
b_box_geometry_from_dict = BBoxGeometry.from_dict(b_box_geometry_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


