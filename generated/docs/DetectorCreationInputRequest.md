# DetectorCreationInputRequest

Helper serializer for validating POST /detectors input.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | A short, descriptive name for the detector. | 
**query** | **str** | A question about the image. | 
**group_name** | **str** | Which group should this detector be part of? | [optional] 
**confidence_threshold** | **float** | If the detector&#39;s prediction is below this confidence threshold, send the image query for human review. | [optional] [default to 0.9]
**patience_time** | **float** | How long Groundlight will attempt to generate a confident prediction | [optional] [default to 30.0]
**pipeline_config** | **str** | (Advanced usage) Configuration needed to instantiate a prediction pipeline. | [optional] 
**metadata** | **str** | Base64-encoded metadata for the detector. This should be a JSON object with string keys. The size after encoding should not exceed 1362 bytes, corresponding to 1KiB before encoding. | [optional] 
**mode** | [**ModeEnum**](ModeEnum.md) | Mode in which this detector will work.  * &#x60;BINARY&#x60; - BINARY * &#x60;COUNT&#x60; - COUNT * &#x60;MULTI_CLASS&#x60; - MULTI_CLASS * &#x60;TEXT&#x60; - TEXT * &#x60;BOUNDING_BOX&#x60; - BOUNDING_BOX | [optional] 
**mode_configuration** | [**DetectorCreationInputRequestModeConfiguration**](DetectorCreationInputRequestModeConfiguration.md) |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.detector_creation_input_request import DetectorCreationInputRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DetectorCreationInputRequest from a JSON string
detector_creation_input_request_instance = DetectorCreationInputRequest.from_json(json)
# print the JSON string representation of the object
print DetectorCreationInputRequest.to_json()

# convert the object into a dict
detector_creation_input_request_dict = detector_creation_input_request_instance.to_dict()
# create an instance of DetectorCreationInputRequest from a dict
detector_creation_input_request_from_dict = DetectorCreationInputRequest.from_dict(detector_creation_input_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


