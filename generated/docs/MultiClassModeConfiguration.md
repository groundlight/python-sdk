# MultiClassModeConfiguration


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**class_names** | **List[str]** |  | 
**num_classes** | **int** |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.multi_class_mode_configuration import MultiClassModeConfiguration

# TODO update the JSON string below
json = "{}"
# create an instance of MultiClassModeConfiguration from a JSON string
multi_class_mode_configuration_instance = MultiClassModeConfiguration.from_json(json)
# print the JSON string representation of the object
print MultiClassModeConfiguration.to_json()

# convert the object into a dict
multi_class_mode_configuration_dict = multi_class_mode_configuration_instance.to_dict()
# create an instance of MultiClassModeConfiguration from a dict
multi_class_mode_configuration_from_dict = MultiClassModeConfiguration.from_dict(multi_class_mode_configuration_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


