# CountingResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**confidence** | **float** |  | [optional] 
**source** | **str** |  | [optional] 
**result_type** | **str** |  | [optional] 
**from_edge** | **bool** |  | [optional] 
**count** | **int** |  | 
**greater_than_max** | **bool** |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.counting_result import CountingResult

# TODO update the JSON string below
json = "{}"
# create an instance of CountingResult from a JSON string
counting_result_instance = CountingResult.from_json(json)
# print the JSON string representation of the object
print(CountingResult.to_json())

# convert the object into a dict
counting_result_dict = counting_result_instance.to_dict()
# create an instance of CountingResult from a dict
counting_result_from_dict = CountingResult.from_dict(counting_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


