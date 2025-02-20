# Rule


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [readonly] 
**detector_id** | **str** |  | [readonly] 
**detector_name** | **str** |  | [readonly] 
**name** | **str** |  | 
**condition** | [**Condition**](Condition.md) |  | 
**enabled** | **bool** |  | [optional]  if omitted the server will use the default value of True
**snooze_time_enabled** | **bool** |  | [optional]  if omitted the server will use the default value of False
**snooze_time_value** | **int** |  | [optional]  if omitted the server will use the default value of 0
**snooze_time_unit** | **bool, date, datetime, dict, float, int, list, str, none_type** |  | [optional] 
**human_review_required** | **bool** |  | [optional]  if omitted the server will use the default value of False
**action** | **bool, date, datetime, dict, float, int, list, str, none_type** |  | [optional] 
**webhook_action** | [**[WebhookAction]**](WebhookAction.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


