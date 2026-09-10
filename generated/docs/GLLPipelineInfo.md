# GLLPipelineInfo

Durable build status and, once ready, ONNX model URLs.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**build_key** | **str** |  | 
**status** | [**Status638Enum**](Status638Enum.md) |  | 
**attempt_count** | **int** |  | 
**model_binary_id** | **str** |  | 
**oodd_model_binary_id** | **str, none_type** |  | 
**oodd_model_url** | **str, none_type** |  | 
**pipeline_type** | **str** |  | 
**detector_mode** | **str** |  | 
**stale_from_status** | [**StaleFromStatusEnum**](StaleFromStatusEnum.md) |  | [optional] 
**generation** | **int, none_type** |  | [optional] 
**task_id** | **str, none_type** |  | [optional] 
**model_url** | **str, none_type** |  | [optional] 
**manifest_url** | **str, none_type** |  | [optional] 
**error_code** | **str, none_type** |  | [optional] 
**error_message** | **str, none_type** |  | [optional] 
**updated_at** | **datetime, none_type** |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


