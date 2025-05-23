# EdgeModelInfo

Information for the model running on edge, including temporary presigned urls to the model binaries

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**model_binary_id** | **str** |  | [optional] 
**model_binary_url** | **str** |  | [optional] 
**oodd_model_binary_id** | **str** |  | [optional] 
**oodd_model_binary_url** | **str** |  | [optional] 
**pipeline_config** | **object** |  | [optional] 
**oodd_pipeline_config** | **object** |  | [optional] 
**predictor_metadata** | **object** |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.edge_model_info import EdgeModelInfo

# TODO update the JSON string below
json = "{}"
# create an instance of EdgeModelInfo from a JSON string
edge_model_info_instance = EdgeModelInfo.from_json(json)
# print the JSON string representation of the object
print(EdgeModelInfo.to_json())

# convert the object into a dict
edge_model_info_dict = edge_model_info_instance.to_dict()
# create an instance of EdgeModelInfo from a dict
edge_model_info_from_dict = EdgeModelInfo.from_dict(edge_model_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


