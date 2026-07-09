# ApiToken


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | An nickname for the API token. This name must be unique for this user. | 
**raw_key_snippet** | **str** | Since we&#39;re storing hashed keys, it can be useful to see the raw prefix snippet of the token. | [readonly] 
**created_at** | **datetime** | When was this token created? | [readonly] 
**last_used_at** | **datetime** | The most recent time this API token was used. (Helpful for detecting suspicious activity). | [readonly] 
**expires_at** | **datetime, none_type** | When does this token expire? If Null, the token never expires. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


