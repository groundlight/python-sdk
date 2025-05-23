# Detector

Groundlight Detectors provide answers to natural language questions about images.  Each detector can answer a single question, and multiple detectors can be strung together for more complex logic. Detectors can be created through the create_detector method, or through the create_[MODE]_detector methods for pro tier users

#### Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | A unique ID for this object. | [readonly] 
**type** | **object** | The type of this object. | [readonly] 
**created_at** | **datetime** | When this detector was created. | [readonly] 
**name** | **str** | A short, descriptive name for the detector. | 
**query** | **str** | A question about the image. | [readonly] 
**group_name** | **str** | Which group should this detector be part of? | [readonly] 
**confidence_threshold** | **int, float** | If the detector&#x27;s prediction is below this confidence threshold, send the image query for human review. | [optional]  if omitted the server will use the default value of 0.9
**patience_time** | **int, float** | How long Groundlight will attempt to generate a confident prediction | [optional]  if omitted the server will use the default value of 30.0
**metadata** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}, none_type** | Metadata about the detector. | [readonly] 
**mode** | **str** |  | [readonly] 
**mode_configuration** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}, none_type** |  | [readonly] 
**status** | **object** |  | [optional] 
**escalation_type** | **str** |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

