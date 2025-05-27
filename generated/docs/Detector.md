# Detector

Groundlight Detectors provide answers to natural language questions about images.  Each detector can answer a single question, and multiple detectors can be strung together for more complex logic. Detectors can be created through the create_detector method, or through the create_[MODE]_detector methods for pro tier users

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | A unique ID for this object. | [readonly] 
**type** | [**DetectorTypeEnum**](DetectorTypeEnum.md) | The type of this object. | [readonly] 
**created_at** | **datetime** | When this detector was created. | [readonly] 
**name** | **str** | A short, descriptive name for the detector. | 
**query** | **str** | A question about the image. | [readonly] 
**group_name** | **str** | Which group should this detector be part of? | [readonly] 
**confidence_threshold** | **float** | If the detector&#39;s prediction is below this confidence threshold, send the image query for human review. | [optional] [default to 0.9]
**patience_time** | **float** | How long Groundlight will attempt to generate a confident prediction | [optional] [default to 30.0]
**metadata** | **Dict[str, object]** | Metadata about the detector. | [readonly] 
**mode** | **str** |  | [readonly] 
**mode_configuration** | **Dict[str, object]** |  | [readonly] 
**status** | [**DetectorStatus**](DetectorStatus.md) |  | [optional] 
**escalation_type** | **str** |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.detector import Detector

# TODO update the JSON string below
json = "{}"
# create an instance of Detector from a JSON string
detector_instance = Detector.from_json(json)
# print the JSON string representation of the object
print Detector.to_json()

# convert the object into a dict
detector_dict = detector_instance.to_dict()
# create an instance of Detector from a dict
detector_from_dict = Detector.from_dict(detector_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


