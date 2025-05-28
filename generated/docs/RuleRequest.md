# RuleRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**enabled** | **bool** |  | [optional] [default to True]
**snooze_time_enabled** | **bool** |  | [optional] [default to False]
**snooze_time_value** | **int** |  | [optional] [default to 0]
**snooze_time_unit** | [**SnoozeTimeUnitEnum**](SnoozeTimeUnitEnum.md) |  | [optional] 
**human_review_required** | **bool** |  | [optional] [default to False]
**condition** | [**ConditionRequest**](ConditionRequest.md) |  | 
**action** | [**RuleAction**](RuleAction.md) |  | [optional] 
**webhook_action** | [**List[WebhookActionRequest]**](WebhookActionRequest.md) |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.rule_request import RuleRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RuleRequest from a JSON string
rule_request_instance = RuleRequest.from_json(json)
# print the JSON string representation of the object
print RuleRequest.to_json()

# convert the object into a dict
rule_request_dict = rule_request_instance.to_dict()
# create an instance of RuleRequest from a dict
rule_request_from_dict = RuleRequest.from_dict(rule_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


