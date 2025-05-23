# GetDetectorMetrics200ResponseSummary


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**num_ground_truth** | **int** |  | [optional] 
**num_current_source_human** | **int** |  | [optional] 
**class_counts** | [**GetDetectorMetrics200ResponseSummaryClassCounts**](GetDetectorMetrics200ResponseSummaryClassCounts.md) |  | [optional] 
**unconfident_counts** | **object** |  | [optional] 
**total_iqs** | **int** |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.get_detector_metrics200_response_summary import GetDetectorMetrics200ResponseSummary

# TODO update the JSON string below
json = "{}"
# create an instance of GetDetectorMetrics200ResponseSummary from a JSON string
get_detector_metrics200_response_summary_instance = GetDetectorMetrics200ResponseSummary.from_json(json)
# print the JSON string representation of the object
print(GetDetectorMetrics200ResponseSummary.to_json())

# convert the object into a dict
get_detector_metrics200_response_summary_dict = get_detector_metrics200_response_summary_instance.to_dict()
# create an instance of GetDetectorMetrics200ResponseSummary from a dict
get_detector_metrics200_response_summary_from_dict = GetDetectorMetrics200ResponseSummary.from_dict(get_detector_metrics200_response_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


