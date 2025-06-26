# PaginatedImageQueryList


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | 
**next** | **str** |  | [optional] 
**previous** | **str** |  | [optional] 
**results** | [**List[ImageQuery]**](ImageQuery.md) |  | 

## Example

```python
from groundlight_openapi_client.models.paginated_image_query_list import PaginatedImageQueryList

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedImageQueryList from a JSON string
paginated_image_query_list_instance = PaginatedImageQueryList.from_json(json)
# print the JSON string representation of the object
print PaginatedImageQueryList.to_json()

# convert the object into a dict
paginated_image_query_list_dict = paginated_image_query_list_instance.to_dict()
# create an instance of PaginatedImageQueryList from a dict
paginated_image_query_list_from_dict = PaginatedImageQueryList.from_dict(paginated_image_query_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


