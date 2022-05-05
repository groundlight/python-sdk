# Detector

Spec for serializing a detector object in the public API.

#### Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | A unique ID for this object. | [readonly] 
**type** | **object** | The type of this object. | [readonly] 
**created_at** | **datetime** | When was this detector created? | [readonly] 
**name** | **str** | A short, descriptive name for the detector. | 
**query** | **str** | A question about the image. | [readonly] 
**group_name** | **str** | Which group should this detector be part of? | [readonly] 
**confidence_threshold** | **int, float** | If our detector&#x27;s prediction is below this confidence threshold, send the image query for human review. | [optional]  if omitted the server will use the default value of 0.9
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

