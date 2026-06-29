# VlmVerification

Response shape for POST /v1/vlm-verifications.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [readonly] 
**type** | **str** |  | [readonly] 
**created_at** | **datetime** |  | [readonly] 
**query** | **str** |  | 
**model_id** | **str** |  | 
**result** | [**VlmVerificationResult**](VlmVerificationResult.md) |  | 
**cost** | [**VlmVerificationCost**](VlmVerificationCost.md) |  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


