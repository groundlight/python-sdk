# RuleBase

Base spec for serializing a rule object in the public API.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**detector_id** | **str** | Which detector should this rule be associated with? | [optional] 
**name** | **str** | A short, descriptive name for the rule. | [optional] 
**enabled** | **bool** | Is this rule enabled? | [optional]  if omitted the server will use the default value of True
**snooze_time_enabled** | **bool** | Is this rule snooze time enabled? | [optional]  if omitted the server will use the default value of False
**snooze_time_value** | **int** | How long to snooze the rule for (in seconds). | [optional]  if omitted the server will use the default value of 1
**snooze_time_unit** | **str** | What unit of time to use for the snooze time. | [optional]  if omitted the server will use the default value of "DAYS"
**action** | [**Action**](Action.md) |  | [optional] 
**condition** | [**Condition**](Condition.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


