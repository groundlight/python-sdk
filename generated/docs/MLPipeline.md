# MLPipeline

A single ML pipeline attached to a detector. Includes training status and metrics for the Pipeline Details UI.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [readonly] 
**pipeline_config** | **str** | Get the resolved pipeline config, including defaults. | [readonly] 
**is_active_pipeline** | **bool** | If True, this is the pipeline is used for inference, active learning, etc. for its parent Predictor. | [readonly] 
**is_edge_pipeline** | **bool** | If True, this pipeline is enabled for edge inference. | [readonly] 
**is_unclear_pipeline** | **bool** | If True, this pipeline is used to train classifier for human unclear label prediction. | [readonly] 
**is_oodd_pipeline** | **bool** | If True, this pipeline is used for OODD. | [readonly] 
**is_enabled** | **bool** | If False, this pipeline will not be run for any use case. | [readonly] 
**created_at** | **datetime** |  | [readonly] 
**trained_at** | **datetime, none_type** |  | [readonly] 
**type** | **str** | Determine the pipeline type (active, shadow, unclear, oodd). | [readonly] 
**friendly_name** | **str, none_type** | Get the friendly name from the MLBinary. | [readonly] 
**model_binary_id** | **str, none_type** |  | 
**training_in_progress** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}, none_type** | Check if training is currently in progress for this pipeline. | [readonly] 
**metrics** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** | Get the metrics for this pipeline from MLBinary metadata and evaluation results. | [readonly] 
**eval_mlbinary_key** | **str, none_type** | Get the MLBinary key that was evaluated. | [readonly] 
**eval_mlbinary_revision_number** | **int, none_type** | Get the revision number of the MLBinary that was evaluated. | [readonly] 
**eval_mlbinary_friendly_name** | **str, none_type** | Get the friendly name of the MLBinary that was evaluated. | [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


