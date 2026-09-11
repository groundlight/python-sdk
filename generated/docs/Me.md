# Me

Authenticated user identity from GET /v1/me (email, username, group, is_superuser).

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **str** | Email address of the authenticated user. | 
**username** | **str** | Username of the authenticated user. | 
**group** | **bool, date, datetime, dict, float, int, list, str, none_type** | The group the authenticated user belongs to. | 
**is_superuser** | **bool** | Whether the authenticated user has elevated (superuser) permissions. | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


