# MultiClassificationResult


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**confidence** | **float** |  | [optional] 
**source** | **str** |  | [optional] 
**result_type** | **str** |  | [optional] 
**from_edge** | **bool** |  | [optional] 
**label** | **str** |  | 

## Example

```python
from groundlight_openapi_client.models.multi_classification_result import MultiClassificationResult

# TODO update the JSON string below
json = "{}"
# create an instance of MultiClassificationResult from a JSON string
multi_classification_result_instance = MultiClassificationResult.from_json(json)
# print the JSON string representation of the object
print MultiClassificationResult.to_json()

# convert the object into a dict
multi_classification_result_dict = multi_classification_result_instance.to_dict()
# create an instance of MultiClassificationResult from a dict
multi_classification_result_from_dict = MultiClassificationResult.from_dict(multi_classification_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


