# ImageQuery

ImageQuery objects are the answers to natural language questions about images created by detectors.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metadata** | **Dict[str, object]** | Metadata about the image query. | [readonly] 
**id** | **str** | A unique ID for this object. | [readonly] 
**type** | [**ImageQueryTypeEnum**](ImageQueryTypeEnum.md) | The type of this object. | [readonly] 
**created_at** | **datetime** | When was this detector created? | [readonly] 
**query** | **str** | A question about the image. | [readonly] 
**detector_id** | **str** | Which detector was used on this image query? | [readonly] 
**result_type** | [**ResultTypeEnum**](ResultTypeEnum.md) | What type of result are we returning? | [readonly] 
**result** | [**ImageQueryResult**](ImageQueryResult.md) |  | 
**patience_time** | **float** | How long to wait for a confident response. | [readonly] 
**confidence_threshold** | **float** | Min confidence needed to accept the response of the image query. | [readonly] 
**rois** | [**List[ROI]**](ROI.md) | An array of regions of interest (bounding boxes) collected on image | [readonly] 
**text** | **str** | A text field on image query. | [readonly] 
**done_processing** | **bool** | EDGE ONLY - Whether the image query has completed escalating and will receive no new results. | [optional] [default to False]

## Example

```python
from groundlight_openapi_client.models.image_query import ImageQuery

# TODO update the JSON string below
json = "{}"
# create an instance of ImageQuery from a JSON string
image_query_instance = ImageQuery.from_json(json)
# print the JSON string representation of the object
print ImageQuery.to_json()

# convert the object into a dict
image_query_dict = image_query_instance.to_dict()
# create an instance of ImageQuery from a dict
image_query_from_dict = ImageQuery.from_dict(image_query_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


