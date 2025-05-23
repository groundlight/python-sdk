# NoteRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | **str** | Text content of the note. | [optional] 
**is_pinned** | **bool** |  | [optional] 
**image** | **bytearray** |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.note_request import NoteRequest

# TODO update the JSON string below
json = "{}"
# create an instance of NoteRequest from a JSON string
note_request_instance = NoteRequest.from_json(json)
# print the JSON string representation of the object
print(NoteRequest.to_json())

# convert the object into a dict
note_request_dict = note_request_instance.to_dict()
# create an instance of NoteRequest from a dict
note_request_from_dict = NoteRequest.from_dict(note_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


