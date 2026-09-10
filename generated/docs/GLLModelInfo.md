# GLLModelInfo

Lightweight pointer used by GLL clients to detect when the server has a newer model binary than the one they have cached locally. No S3 calls, no pre-signed URLs - one DB read.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**model_binary_id** | **str** |  | 
**mode** | **str** |  | 
**oodd_model_binary_id** | **str, none_type** |  | [optional] 
**updated_at** | **datetime, none_type** |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


