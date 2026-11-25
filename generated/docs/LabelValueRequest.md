# LabelValueRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**label** | **str, none_type** |  | 
**image_query_id** | **str** |  | 
**confidence** | **float** | Confidence of the edge model&#39;s answer. Required on edge labels and not accepted otherwise. | [optional] 
**rois** | [**[ROIRequest], none_type**](ROIRequest.md) | On edge labels, required for bounding box and count detectors (an empty list when the model found nothing) and not accepted for other detectors. | [optional] 
**from_edge** | **bool** | Store this label as the answer an edge model gave for the image query. | [optional]  if omitted the server will use the default value of False
**model_binary_id** | **str** | ID of the edge model binary that gave this answer. Required on edge labels and not accepted otherwise. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


