# ConditionRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**verb** | **str** |  | 
**parameters** | **Dict[str, object]** |  | 

## Example

```python
from groundlight_openapi_client.models.condition_request import ConditionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ConditionRequest from a JSON string
condition_request_instance = ConditionRequest.from_json(json)
# print the JSON string representation of the object
print ConditionRequest.to_json()

# convert the object into a dict
condition_request_dict = condition_request_instance.to_dict()
# create an instance of ConditionRequest from a dict
condition_request_from_dict = ConditionRequest.from_dict(condition_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


