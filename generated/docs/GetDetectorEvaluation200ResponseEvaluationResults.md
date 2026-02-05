# GetDetectorEvaluation200ResponseEvaluationResults


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**eval_timestamp** | **datetime** |  | [optional] 
**total_ground_truth_examples** | **int** |  | [optional] 
**total_labeled_examples** | **int** |  | [optional] 
**kfold_pooled__balanced_accuracy** | **float** |  | [optional] 
**kfold_pooled__positive_accuracy** | **float** |  | [optional] 
**kfold_pooled__negative_accuracy** | **float** |  | [optional] 
**precision__mean** | **float** |  | [optional] 
**recall__mean** | **float** |  | [optional] 
**roc_auc__mean** | **float** |  | [optional] 
**balanced_system_accuracies** | **Dict[str, object]** |  | [optional] 
**positive_system_accuracies** | **Dict[str, object]** |  | [optional] 
**negative_system_accuracies** | **Dict[str, object]** |  | [optional] 
**mean_absolute_error__mean** | **float** |  | [optional] 
**objdet_precision__mean** | **float** |  | [optional] 
**objdet_recall__mean** | **float** |  | [optional] 
**objdet_f1_score__mean** | **float** |  | [optional] 
**class_accuracies** | **Dict[str, object]** |  | [optional] 
**confusion_dict** | **Dict[str, object]** |  | [optional] 
**num_examples_per_class** | **Dict[str, object]** |  | [optional] 

## Example

```python
from groundlight_openapi_client.models.get_detector_evaluation200_response_evaluation_results import GetDetectorEvaluation200ResponseEvaluationResults

# TODO update the JSON string below
json = "{}"
# create an instance of GetDetectorEvaluation200ResponseEvaluationResults from a JSON string
get_detector_evaluation200_response_evaluation_results_instance = GetDetectorEvaluation200ResponseEvaluationResults.from_json(json)
# print the JSON string representation of the object
print(GetDetectorEvaluation200ResponseEvaluationResults.to_json())

# convert the object into a dict
get_detector_evaluation200_response_evaluation_results_dict = get_detector_evaluation200_response_evaluation_results_instance.to_dict()
# create an instance of GetDetectorEvaluation200ResponseEvaluationResults from a dict
get_detector_evaluation200_response_evaluation_results_from_dict = GetDetectorEvaluation200ResponseEvaluationResults.from_dict(get_detector_evaluation200_response_evaluation_results_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


