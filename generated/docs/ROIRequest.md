# ROIRequest

Mixin for serializers to handle data in the StrictBaseModel format

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**label** | **str** | The label of the bounding box. | 
**geometry** | [**BBoxGeometryRequest**](BBoxGeometryRequest.md) |  | 

## Example

```python
from groundlight_openapi_client.models.roi_request import ROIRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ROIRequest from a JSON string
roi_request_instance = ROIRequest.from_json(json)
# print the JSON string representation of the object
print(ROIRequest.to_json())

# convert the object into a dict
roi_request_dict = roi_request_instance.to_dict()
# create an instance of ROIRequest from a dict
roi_request_from_dict = ROIRequest.from_dict(roi_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


