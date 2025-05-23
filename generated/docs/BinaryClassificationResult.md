# BinaryClassificationResult


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
from groundlight_openapi_client.models.binary_classification_result import BinaryClassificationResult

# TODO update the JSON string below
json = "{}"
# create an instance of BinaryClassificationResult from a JSON string
binary_classification_result_instance = BinaryClassificationResult.from_json(json)
# print the JSON string representation of the object
print(BinaryClassificationResult.to_json())

# convert the object into a dict
binary_classification_result_dict = binary_classification_result_instance.to_dict()
# create an instance of BinaryClassificationResult from a dict
binary_classification_result_from_dict = BinaryClassificationResult.from_dict(binary_classification_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


