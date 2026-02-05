# WebhookAction


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**url** | **str** |  | 
**include_image** | **bool** |  | [optional] 
**payload_template** | [**PayloadTemplate**](PayloadTemplate.md) |  | [optional] 
**last_message_failed** | **bool** |  | [optional] 
**last_failure_error** | **str** |  | [optional] 
**last_failed_at** | **datetime** |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.webhook_action import WebhookAction

# TODO update the JSON string below
json = "{}"
# create an instance of WebhookAction from a JSON string
webhook_action_instance = WebhookAction.from_json(json)
# print the JSON string representation of the object
print(WebhookAction.to_json())

# convert the object into a dict
webhook_action_dict = webhook_action_instance.to_dict()
# create an instance of WebhookAction from a dict
webhook_action_from_dict = WebhookAction.from_dict(webhook_action_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


