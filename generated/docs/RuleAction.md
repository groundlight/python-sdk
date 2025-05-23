# RuleAction


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**channel** | [**ChannelEnum**](ChannelEnum.md) |  | 
**recipient** | **str** |  | 
**include_image** | **bool** |  | 

## Example

```python
from groundlight_openapi_client.models.rule_action import RuleAction

# TODO update the JSON string below
json = "{}"
# create an instance of RuleAction from a JSON string
rule_action_instance = RuleAction.from_json(json)
# print the JSON string representation of the object
print(RuleAction.to_json())

# convert the object into a dict
rule_action_dict = rule_action_instance.to_dict()
# create an instance of RuleAction from a dict
rule_action_from_dict = RuleAction.from_dict(rule_action_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


