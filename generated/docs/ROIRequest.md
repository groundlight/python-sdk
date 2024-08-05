# ROIRequest

A serializer for ROI objects. Corresponds directly with predictors.types.ROI  The class should handle like a normal serializer, just note that the when instantiating as ROISerializer(instance=obj), the obj is the json representation pulled straight from the database

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**label** | **str** | The label of the bounding box. | 
**geometry** | [**BBoxGeometryRequest**](BBoxGeometryRequest.md) |  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


