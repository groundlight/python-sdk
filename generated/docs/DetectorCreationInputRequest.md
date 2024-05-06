# DetectorCreationInputRequest

Helper serializer for validating POST /detectors input.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | A short, descriptive name for the detector. | 
**query** | **str** | A question about the image. | 
**group_name** | **str** | Which group should this detector be part of? | [optional] 
**confidence_threshold** | **float** | If the detector&#39;s prediction is below this confidence threshold, send the image query for human review. | [optional]  if omitted the server will use the default value of 0.9
**patience_time** | **float** | How long Groundlight will attempt to generate a confident prediction | [optional]  if omitted the server will use the default value of 30.0
**pipeline_config** | **str, none_type** | (Advanced usage) Configuration needed to instantiate a prediction pipeline. | [optional] 
**metadata** | **str** | Base64-encoded metadata for the detector. This should be a JSON object with string keys. The size after encoding should not exceed 1362 bytes, corresponding to 1KiB before encoding. | [optional] 
**mode** | **bool, date, datetime, dict, float, int, list, str, none_type** | Mode in which this detector will work.  * &#x60;BINARY&#x60; - BINARY * &#x60;COUNT&#x60; - COUNT | [optional] 
**mode_configuration** | **bool, date, datetime, dict, float, int, list, str, none_type** | Configuration for each detector mode. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


