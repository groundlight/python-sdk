# PatchedDetectorRequest

Spec for serializing a detector object in the public API.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | A short, descriptive name for the detector. | [optional] 
**confidence_threshold** | **float** | If the detector&#39;s prediction is below this confidence threshold, send the image query for human review. | [optional]  if omitted the server will use the default value of 0.9
**patience_time** | **float** | How long Groundlight will attempt to generate a confident prediction | [optional]  if omitted the server will use the default value of 30.0
**status** | **bool, date, datetime, dict, float, int, list, str, none_type** |  | [optional] 
**escalation_type** | **bool, date, datetime, dict, float, int, list, str, none_type** | Category that define internal proccess for labeling image queries  * &#x60;STANDARD&#x60; - STANDARD * &#x60;NO_HUMAN_LABELING&#x60; - NO_HUMAN_LABELING | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


