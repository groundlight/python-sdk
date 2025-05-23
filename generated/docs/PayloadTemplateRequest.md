# PayloadTemplateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**template** | **str** |  | 
**headers** | **Dict[str, str]** |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.payload_template_request import PayloadTemplateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PayloadTemplateRequest from a JSON string
payload_template_request_instance = PayloadTemplateRequest.from_json(json)
# print the JSON string representation of the object
print(PayloadTemplateRequest.to_json())

# convert the object into a dict
payload_template_request_dict = payload_template_request_instance.to_dict()
# create an instance of PayloadTemplateRequest from a dict
payload_template_request_from_dict = PayloadTemplateRequest.from_dict(payload_template_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


