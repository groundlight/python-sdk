# Me

Authenticated user identity from GET /v1/me (id, email, username, groups).

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | Numeric id of the authenticated user. | 
**email** | **str** | Email address of the authenticated user. | 
**username** | **str** | Username of the authenticated user. | 
**groups** | [**[CustomerGroup]**](CustomerGroup.md) | Customer groups the authenticated user belongs to. | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


