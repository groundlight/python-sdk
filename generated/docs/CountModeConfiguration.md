# CountModeConfiguration


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**max_count** | **int** |  | [optional] 
**class_name** | **str** |  | 

## Example

```python
from groundlight_openapi_client.models.count_mode_configuration import CountModeConfiguration

# TODO update the JSON string below
json = "{}"
# create an instance of CountModeConfiguration from a JSON string
count_mode_configuration_instance = CountModeConfiguration.from_json(json)
# print the JSON string representation of the object
print(CountModeConfiguration.to_json())

# convert the object into a dict
count_mode_configuration_dict = count_mode_configuration_instance.to_dict()
# create an instance of CountModeConfiguration from a dict
count_mode_configuration_from_dict = CountModeConfiguration.from_dict(count_mode_configuration_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


