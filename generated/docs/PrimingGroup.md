# PrimingGroup

A PrimingGroup owned by the authenticated user.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [readonly] 
**name** | **str** |  | 
**num_classes** | **int, none_type** | Number of output classes this priming group is trained for. Set automatically from the source predictor when created via create_user_priming_group (MULTI_CLASS only). Nullable for legacy rows and for modes where class count isn&#39;t meaningful; a follow-up PR will tighten this after manual backfill. | [readonly] 
**is_global** | **bool** | If True, this priming group is shared to all Groundlight users. Can only be set by Groundlight admins. | [readonly] 
**created_at** | **datetime** |  | [readonly] 
**detector_mode** | **bool, date, datetime, dict, float, int, list, str, none_type** | Detector mode this priming group is intended for (BINARY, MULTI_CLASS, etc.). Validated against the pipeline_config of every active and shadow base MLBinary in clean(). Nullable only for legacy rows pre-dating this field; new PrimingGroups must set it.  * &#x60;BINARY&#x60; - BINARY * &#x60;COUNT&#x60; - COUNT * &#x60;MULTI_CLASS&#x60; - MULTI_CLASS * &#x60;TEXT&#x60; - TEXT * &#x60;BOUNDING_BOX&#x60; - BOUNDING_BOX | [optional] 
**canonical_query** | **str, none_type** | Canonical semantic query for this priming group | [optional] 
**active_pipeline_config** | **str, none_type** | Active pipeline config override for new detectors created in this priming group. If set, this overrides the default active pipeline config at creation time.Can be either a pipeline name or full config string. | [optional] 
**priming_group_specific_shadow_pipeline_configs** | **bool, date, datetime, dict, float, int, list, str, none_type** | Configs for shadow pipelines to create for detectors in this priming group. These are added to the default shadow pipeline configs for a detector of the given mode. Each entry is either a pipeline name or full config string.  | [optional] 
**disable_shadow_pipelines** | **bool** | If True, new detectors added to this priming group will not receive the mode-specific default shadow pipelines from INITIAL_SHADOW_PIPELINE_CONFIG_SET. Priming-group-specific shadow configs still apply. Use this to guarantee the primed active MLBinary is never switched off by a shadow pipeline being promoted. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


