# GetDetectorMetrics200ResponseSummaryClassCounts


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**source_ml** | **object** |  | [optional] 
**source_human** | **object** |  | [optional] 
**cloud_labeler** | **object** |  | [optional] 
**cloud** | **object** |  | [optional] 
**total** | **object** |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.get_detector_metrics200_response_summary_class_counts import GetDetectorMetrics200ResponseSummaryClassCounts

# TODO update the JSON string below
json = "{}"
# create an instance of GetDetectorMetrics200ResponseSummaryClassCounts from a JSON string
get_detector_metrics200_response_summary_class_counts_instance = GetDetectorMetrics200ResponseSummaryClassCounts.from_json(json)
# print the JSON string representation of the object
print GetDetectorMetrics200ResponseSummaryClassCounts.to_json()

# convert the object into a dict
get_detector_metrics200_response_summary_class_counts_dict = get_detector_metrics200_response_summary_class_counts_instance.to_dict()
# create an instance of GetDetectorMetrics200ResponseSummaryClassCounts from a dict
get_detector_metrics200_response_summary_class_counts_from_dict = GetDetectorMetrics200ResponseSummaryClassCounts.from_dict(get_detector_metrics200_response_summary_class_counts_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


