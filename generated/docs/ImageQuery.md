# ImageQuery

Spec for serializing a image-query object in the public API.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | A unique ID for this object. | [readonly] 
**type** | **bool, date, datetime, dict, float, int, list, str, none_type** | The type of this object. | [readonly] 
**created_at** | **datetime** | When was this detector created? | [readonly] 
**query** | **str** | A question about the image. | [readonly] 
**detector_id** | **str** | Which detector was used on this image query? | [readonly] 
**result_type** | **bool, date, datetime, dict, float, int, list, str, none_type** | What type of result are we returning? | [readonly] 
**result** | **bool, date, datetime, dict, float, int, list, str, none_type** |  | [optional] [readonly] 
**confidence_threshold** | **float** |  | [optional] [readonly] 
**metadata** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}, none_type** | A dictionary of custom key/value metadata to associate with the image query (limited to 1KB). | [optional] [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


