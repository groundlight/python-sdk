# LabelValue


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**confidence** | **float** |  | [readonly] 
**class_name** | **str** | Return a human-readable class name for this label (e.g. YES/NO) | [readonly] 
**rois** | [**List[ROI]**](ROI.md) |  | [optional] 
**annotations_requested** | **List[str]** |  | [readonly] 
**created_at** | **datetime** |  | [readonly] 
**detector_id** | **int** |  | [readonly] 
**source** | **str** |  | [readonly] 
**text** | **str** | Text annotations | [readonly] 

## Example

```python
from groundlight_openapi_client.models.label_value import LabelValue

# TODO update the JSON string below
json = "{}"
# create an instance of LabelValue from a JSON string
label_value_instance = LabelValue.from_json(json)
# print the JSON string representation of the object
print(LabelValue.to_json())

# convert the object into a dict
label_value_dict = label_value_instance.to_dict()
# create an instance of LabelValue from a dict
label_value_from_dict = LabelValue.from_dict(label_value_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


