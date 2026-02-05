# LabelValueRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**label** | **str** |  | 
**image_query_id** | **str** |  | 
**rois** | [**List[ROIRequest]**](ROIRequest.md) |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.label_value_request import LabelValueRequest

# TODO update the JSON string below
json = "{}"
# create an instance of LabelValueRequest from a JSON string
label_value_request_instance = LabelValueRequest.from_json(json)
# print the JSON string representation of the object
print(LabelValueRequest.to_json())

# convert the object into a dict
label_value_request_dict = label_value_request_instance.to_dict()
# create an instance of LabelValueRequest from a dict
label_value_request_from_dict = LabelValueRequest.from_dict(label_value_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


