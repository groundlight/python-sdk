# PaginatedDetectorList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | 
**next** | **str** |  | [optional] 
**previous** | **str** |  | [optional] 
**results** | [**List[Detector]**](Detector.md) |  | 

## Example

```python
from groundlight_openapi_client.models.paginated_detector_list import PaginatedDetectorList

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedDetectorList from a JSON string
paginated_detector_list_instance = PaginatedDetectorList.from_json(json)
# print the JSON string representation of the object
print(PaginatedDetectorList.to_json())

# convert the object into a dict
paginated_detector_list_dict = paginated_detector_list_instance.to_dict()
# create an instance of PaginatedDetectorList from a dict
paginated_detector_list_from_dict = PaginatedDetectorList.from_dict(paginated_detector_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


