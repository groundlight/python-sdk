# PayloadTemplate


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**template** | **str** |  | 
**headers** | **Dict[str, str]** |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.payload_template import PayloadTemplate

# TODO update the JSON string below
json = "{}"
# create an instance of PayloadTemplate from a JSON string
payload_template_instance = PayloadTemplate.from_json(json)
# print the JSON string representation of the object
print PayloadTemplate.to_json()

# convert the object into a dict
payload_template_dict = payload_template_instance.to_dict()
# create an instance of PayloadTemplate from a dict
payload_template_from_dict = PayloadTemplate.from_dict(payload_template_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


