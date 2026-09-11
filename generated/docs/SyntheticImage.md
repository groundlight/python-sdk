# SyntheticImage

Response shape for POST /v1/synthetic-images.  A passthrough of the synthetic image service's generation result with a correlation `id` added.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [readonly] 
**image** | **str** | Base64-encoded generated PNG. | 
**width** | **int** |  | 
**height** | **int** |  | 
**label** | **str** | Lens-level binary event label: \&quot;YES\&quot; or \&quot;NO\&quot;. | 
**rois** | [**[ROI]**](ROI.md) |  | 
**added_roi_index** | **int** | Index into &#x60;rois&#x60; of the object this request inserted. Every other entry was already in the frame. | 
**metadata** | **bool, date, datetime, dict, float, int, list, str, none_type** | Generation details reported by the generation service. | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


