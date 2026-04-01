# PrimingGroup

A PrimingGroup owned by the authenticated user.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [readonly] 
**name** | **str** |  | 
**is_global** | **bool** | If True, this priming group is shared to all Groundlight users by Groundlight admins. | [readonly] 
**created_at** | **datetime** |  | [readonly] 
**canonical_query** | **str, none_type** | Canonical semantic query for this priming group | [optional] 
**active_pipeline_config** | **str, none_type** | Active pipeline config override for detectors in this priming group. If set, this overrides the default active pipeline config. Can be either a pipeline name or full config string. | [optional] 
**priming_group_specific_shadow_pipeline_configs** | **bool, date, datetime, dict, float, int, list, str, none_type** | Priming group-specific shadow pipeline configs to create for detectors in this priming group. These are added to the default shadow pipeline configs for a detector of the given modeEach entry is either a pipeline name or full config string.  | [optional] 
**disable_shadow_pipelines** | **bool** | If True, new detectors added to this priming group will not receive the mode-specific default shadow pipelines from INITIAL_SHADOW_PIPELINE_CONFIG_SET. Priming-group-specific shadow configs still apply. Use this to guarantee the primed active MLBinary is never switched off by a shadow pipeline being promoted. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


