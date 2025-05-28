# PatchedDetectorRequest

Groundlight Detectors provide answers to natural language questions about images.  Each detector can answer a single question, and multiple detectors can be strung together for more complex logic. Detectors can be created through the create_detector method, or through the create_[MODE]_detector methods for pro tier users

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | A short, descriptive name for the detector. | [optional] 
**confidence_threshold** | **float** | If the detector&#39;s prediction is below this confidence threshold, send the image query for human review. | [optional] [default to 0.9]
**patience_time** | **float** | How long Groundlight will attempt to generate a confident prediction | [optional] [default to 30.0]
**status** | [**DetectorStatus**](DetectorStatus.md) |  | [optional] 
**escalation_type** | **str** |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.patched_detector_request import PatchedDetectorRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PatchedDetectorRequest from a JSON string
patched_detector_request_instance = PatchedDetectorRequest.from_json(json)
# print the JSON string representation of the object
print PatchedDetectorRequest.to_json()

# convert the object into a dict
patched_detector_request_dict = patched_detector_request_instance.to_dict()
# create an instance of PatchedDetectorRequest from a dict
patched_detector_request_from_dict = PatchedDetectorRequest.from_dict(patched_detector_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


