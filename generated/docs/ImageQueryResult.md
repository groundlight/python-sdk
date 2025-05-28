# ImageQueryResult


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**confidence** | **float** |  | [optional] 
**source** | **str** |  | [optional] 
**result_type** | **str** |  | [optional] 
**from_edge** | **bool** |  | [optional] 
**label** | **str** |  | 
**count** | **int** |  | 
**greater_than_max** | **bool** |  | [optional] 
**text** | **str** |  | 
**truncated** | **bool** |  | 

## Example

```python
from groundlight_openapi_client.models.image_query_result import ImageQueryResult

# TODO update the JSON string below
json = "{}"
# create an instance of ImageQueryResult from a JSON string
image_query_result_instance = ImageQueryResult.from_json(json)
# print the JSON string representation of the object
print ImageQueryResult.to_json()

# convert the object into a dict
image_query_result_dict = image_query_result_instance.to_dict()
# create an instance of ImageQueryResult from a dict
image_query_result_from_dict = ImageQueryResult.from_dict(image_query_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


