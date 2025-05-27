# WebhookActionRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**url** | **str** |  | 
**include_image** | **bool** |  | [optional] 
**payload_template** | [**PayloadTemplateRequest**](PayloadTemplateRequest.md) |  | [optional] 
**last_message_failed** | **bool** |  | [optional] 
**last_failure_error** | **str** |  | [optional] 
**last_failed_at** | **datetime** |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.webhook_action_request import WebhookActionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of WebhookActionRequest from a JSON string
webhook_action_request_instance = WebhookActionRequest.from_json(json)
# print the JSON string representation of the object
print WebhookActionRequest.to_json()

# convert the object into a dict
webhook_action_request_dict = webhook_action_request_instance.to_dict()
# create an instance of WebhookActionRequest from a dict
webhook_action_request_from_dict = WebhookActionRequest.from_dict(webhook_action_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


