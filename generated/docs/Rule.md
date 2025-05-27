# Rule


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [readonly] 
**detector_id** | **str** |  | [readonly] 
**detector_name** | **str** |  | [readonly] 
**name** | **str** |  | 
**enabled** | **bool** |  | [optional] [default to True]
**snooze_time_enabled** | **bool** |  | [optional] [default to False]
**snooze_time_value** | **int** |  | [optional] [default to 0]
**snooze_time_unit** | [**SnoozeTimeUnitEnum**](SnoozeTimeUnitEnum.md) |  | [optional] 
**human_review_required** | **bool** |  | [optional] [default to False]
**condition** | [**Condition**](Condition.md) |  | 
**action** | [**RuleAction**](RuleAction.md) |  | [optional] 
**webhook_action** | [**List[WebhookAction]**](WebhookAction.md) |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.rule import Rule

# TODO update the JSON string below
json = "{}"
# create an instance of Rule from a JSON string
rule_instance = Rule.from_json(json)
# print the JSON string representation of the object
print Rule.to_json()

# convert the object into a dict
rule_dict = rule_instance.to_dict()
# create an instance of Rule from a dict
rule_from_dict = Rule.from_dict(rule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


