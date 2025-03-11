# ImageQuery

ImageQuery objects are the answers to natural language questions about images created by detectors.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metadata** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}, none_type** | Metadata about the image query. | [readonly] 
**id** | **str** | A unique ID for this object. | [readonly] 
**type** | **bool, date, datetime, dict, float, int, list, str, none_type** | The type of this object. | [readonly] 
**created_at** | **datetime** | When was this detector created? | [readonly] 
**query** | **str** | A question about the image. | [readonly] 
**detector_id** | **str** | Which detector was used on this image query? | [readonly] 
**result_type** | **bool, date, datetime, dict, float, int, list, str, none_type** | What type of result are we returning? | [readonly] 
**result** | **bool, date, datetime, dict, float, int, list, str, none_type** |  | 
**patience_time** | **float** | How long to wait for a confident response. | [readonly] 
**confidence_threshold** | **float** | Min confidence needed to accept the response of the image query. | [readonly] 
**rois** | [**[ROI], none_type**](ROI.md) | An array of regions of interest (bounding boxes) collected on image | [readonly] 
**text** | **str, none_type** | A text field on image query. | [readonly] 
**done_processing** | **bool** | EDGE ONLY - Whether the image query has completed escalating and will receive no new results. | [optional]  if omitted the server will use the default value of False
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


