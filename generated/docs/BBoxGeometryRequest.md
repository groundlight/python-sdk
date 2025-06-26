# BBoxGeometryRequest

Mixin for serializers to handle data in the StrictBaseModel format

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**left** | **float** |  | 
**top** | **float** |  | 
**right** | **float** |  | 
**bottom** | **float** |  | 

## Example

```python
from groundlight_openapi_client.models.b_box_geometry_request import BBoxGeometryRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BBoxGeometryRequest from a JSON string
b_box_geometry_request_instance = BBoxGeometryRequest.from_json(json)
# print the JSON string representation of the object
print BBoxGeometryRequest.to_json()

# convert the object into a dict
b_box_geometry_request_dict = b_box_geometry_request_instance.to_dict()
# create an instance of BBoxGeometryRequest from a dict
b_box_geometry_request_from_dict = BBoxGeometryRequest.from_dict(b_box_geometry_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


