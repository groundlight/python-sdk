# VerdictCreationInputRequest

Input for adding a verdict to an alert.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**source** | **bool, date, datetime, dict, float, int, list, str, none_type** | Who decided. Only VLM is accepted on this route for now.  * &#x60;VLM&#x60; - VLM * &#x60;HUMAN&#x60; - HUMAN | 
**verdict** | [**AlertVerdictEnum**](AlertVerdictEnum.md) |  | 
**decided_at** | **datetime** | When the reviewer made the decision. | 
**rationale** | **str** | Why the reviewer decided this. | [optional] 
**reviewer** | **str** | Free-form reviewer, such as a model name or your ID for the operator (an ID, not a name). | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


