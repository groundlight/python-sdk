# PaginatedRuleList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**count** | **int** |  | 
**next** | **str** |  | [optional] 
**previous** | **str** |  | [optional] 
**results** | [**List[Rule]**](Rule.md) |  | 

## Example

```python
from groundlight_openapi_client.models.paginated_rule_list import PaginatedRuleList

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedRuleList from a JSON string
paginated_rule_list_instance = PaginatedRuleList.from_json(json)
# print the JSON string representation of the object
print(PaginatedRuleList.to_json())

# convert the object into a dict
paginated_rule_list_dict = paginated_rule_list_instance.to_dict()
# create an instance of PaginatedRuleList from a dict
paginated_rule_list_from_dict = PaginatedRuleList.from_dict(paginated_rule_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


