# User


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | [readonly] 
**username** | **str** | Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. | 
**groups** | [**[Group]**](Group.md) |  | [readonly] 
**is_labeler** | **bool** | Add \&quot;is_labeler\&quot; field outside the django User model, without having to go through the pain of migrating to a custom User model.  https://www.django-rest-framework.org/api-guide/fields/#serializermethodfield | [readonly] 
**userprofile** | **bool, date, datetime, dict, float, int, list, str, none_type** |  | [readonly] 
**accepted_tos** | **bool** | A boolean representing whether or not the user has accepted our terms of service. | [readonly] 
**is_superuser** | **bool** | Designates that this user has all permissions without explicitly assigning them. | [optional] 
**is_staff** | **bool** | Designates whether the user can log into this admin site. | [optional] 
**email** | **str** |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


