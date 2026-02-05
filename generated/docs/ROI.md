# ROI

Mixin for serializers to handle data in the StrictBaseModel format

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**label** | **str** | The label of the bounding box. | 
**score** | **float** | The confidence of the bounding box. | [readonly] 
**geometry** | [**BBoxGeometry**](BBoxGeometry.md) |  | 

## Example

```python
from groundlight_openapi_client.models.roi import ROI

# TODO update the JSON string below
json = "{}"
# create an instance of ROI from a JSON string
roi_instance = ROI.from_json(json)
# print the JSON string representation of the object
print(ROI.to_json())

# convert the object into a dict
roi_dict = roi_instance.to_dict()
# create an instance of ROI from a dict
roi_from_dict = ROI.from_dict(roi_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


