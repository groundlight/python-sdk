# MLPipeline

A single ML pipeline attached to a detector.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [readonly] 
**pipeline_config** | **str, none_type** | configuration needed to instantiate a prediction pipeline. | [readonly] 
**is_active_pipeline** | **bool** | If True, this is the pipeline is used for inference, active learning, etc. for its parent Predictor. | [readonly] 
**is_edge_pipeline** | **bool** | If True, this pipeline is enabled for edge inference. | [readonly] 
**is_unclear_pipeline** | **bool** | If True, this pipeline is used to train classifier for human unclear label prediction. | [readonly] 
**is_oodd_pipeline** | **bool** | If True, this pipeline is used for OODD. | [readonly] 
**is_enabled** | **bool** | If False, this pipeline will not be run for any use case. | [readonly] 
**created_at** | **datetime** |  | [readonly] 
**trained_at** | **datetime, none_type** |  | [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


