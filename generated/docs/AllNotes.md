# AllNotes

Serializes all notes for a given detector, grouped by type as listed in UserProfile.NoteCategoryChoices The fields must match whats in USERPROFILE.NoteCategoryChoices

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**customer** | [**List[Note]**](Note.md) |  | 
**gl** | [**List[Note]**](Note.md) |  | 

## Example

```python
from groundlight_openapi_client.models.all_notes import AllNotes

# TODO update the JSON string below
json = "{}"
# create an instance of AllNotes from a JSON string
all_notes_instance = AllNotes.from_json(json)
# print the JSON string representation of the object
print(AllNotes.to_json())

# convert the object into a dict
all_notes_dict = all_notes_instance.to_dict()
# create an instance of AllNotes from a dict
all_notes_from_dict = AllNotes.from_dict(all_notes_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


