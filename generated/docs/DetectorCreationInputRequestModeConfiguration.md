# DetectorCreationInputRequestModeConfiguration


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**max_count** | **int** |  | [optional] 
**class_name** | **str** |  | 
**class_names** | **List[str]** |  | 
**num_classes** | **int** |  | [optional] 
**value_max_length** | **int** |  | [optional] 
**max_num_bboxes** | **int** |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.detector_creation_input_request_mode_configuration import DetectorCreationInputRequestModeConfiguration

# TODO update the JSON string below
json = "{}"
# create an instance of DetectorCreationInputRequestModeConfiguration from a JSON string
detector_creation_input_request_mode_configuration_instance = DetectorCreationInputRequestModeConfiguration.from_json(json)
# print the JSON string representation of the object
print(DetectorCreationInputRequestModeConfiguration.to_json())

# convert the object into a dict
detector_creation_input_request_mode_configuration_dict = detector_creation_input_request_mode_configuration_instance.to_dict()
# create an instance of DetectorCreationInputRequestModeConfiguration from a dict
detector_creation_input_request_mode_configuration_from_dict = DetectorCreationInputRequestModeConfiguration.from_dict(detector_creation_input_request_mode_configuration_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


