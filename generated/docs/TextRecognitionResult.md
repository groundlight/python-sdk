# TextRecognitionResult


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**confidence** | **float** |  | [optional] 
**source** | **str** |  | [optional] 
**result_type** | **str** |  | [optional] 
**from_edge** | **bool** |  | [optional] 
**text** | **str** |  | 
**truncated** | **bool** |  | 

## Example

```python
from groundlight_openapi_client.models.text_recognition_result import TextRecognitionResult

# TODO update the JSON string below
json = "{}"
# create an instance of TextRecognitionResult from a JSON string
text_recognition_result_instance = TextRecognitionResult.from_json(json)
# print the JSON string representation of the object
print TextRecognitionResult.to_json()

# convert the object into a dict
text_recognition_result_dict = text_recognition_result_instance.to_dict()
# create an instance of TextRecognitionResult from a dict
text_recognition_result_from_dict = TextRecognitionResult.from_dict(text_recognition_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


