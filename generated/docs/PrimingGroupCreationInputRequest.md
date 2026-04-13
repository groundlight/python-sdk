# PrimingGroupCreationInputRequest

Input for creating a new user-owned PrimingGroup seeded from an existing MLPipeline.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name for the new priming group. | 
**source_ml_pipeline_id** | **str** | ID of an MLPipeline owned by this account whose trained model will seed the priming group. | 
**canonical_query** | **str, none_type** | Optional canonical semantic query describing this priming group. | [optional] 
**disable_shadow_pipelines** | **bool** | If true, new detectors added to this priming group will not receive the default shadow pipelines. This guarantees the primed active model is never switched off. | [optional]  if omitted the server will use the default value of False
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


