# PatchedDetectorRequest

Groundlight Detectors provide answers to natural language questions about images.  Each detector can answer a single question, and multiple detectors can be strung together for more complex logic. Detectors can be created through the create_detector method, or through the create_[MODE]_detector methods for pro tier users

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | A short, descriptive name for the detector. | [optional] 
**confidence_threshold** | **float** | If the detector&#39;s prediction is below this confidence threshold, send the image query for human review. | [optional]  if omitted the server will use the default value of 0.9
**patience_time** | **float** | How long Groundlight will attempt to generate a confident prediction | [optional]  if omitted the server will use the default value of 30.0
**status** | **bool, date, datetime, dict, float, int, list, str, none_type** |  | [optional] 
**escalation_type** | **str** |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


