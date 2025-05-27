# groundlight_openapi_client.DetectorsApi

All URIs are relative to *https://api.groundlight.ai/device-api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_detector**](DetectorsApi.md#create_detector) | **POST** /v1/detectors | 
[**delete_detector**](DetectorsApi.md#delete_detector) | **DELETE** /v1/detectors/{id} | 
[**get_detector**](DetectorsApi.md#get_detector) | **GET** /v1/detectors/{id} | 
[**get_detector_evaluation**](DetectorsApi.md#get_detector_evaluation) | **GET** /v1/detectors/{id}/evaluation | 
[**get_detector_metrics**](DetectorsApi.md#get_detector_metrics) | **GET** /v1/detectors/{detector_id}/metrics | 
[**list_detectors**](DetectorsApi.md#list_detectors) | **GET** /v1/detectors | 
[**update_detector**](DetectorsApi.md#update_detector) | **PATCH** /v1/detectors/{id} | 


# **create_detector**
> Detector create_detector(detector_creation_input_request)



Create a new detector.

### Example

* Api Key Authentication (ApiToken):
```python
import time
import os
import groundlight_openapi_client
from groundlight_openapi_client.models.detector import Detector
from groundlight_openapi_client.models.detector_creation_input_request import DetectorCreationInputRequest
from groundlight_openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.groundlight.ai/device-api
# See configuration.py for a list of all supported configuration parameters.
configuration = groundlight_openapi_client.Configuration(
    host = "https://api.groundlight.ai/device-api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: ApiToken
configuration.api_key['ApiToken'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiToken'] = 'Bearer'

# Enter a context with an instance of the API client
with groundlight_openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = groundlight_openapi_client.DetectorsApi(api_client)
    detector_creation_input_request = groundlight_openapi_client.DetectorCreationInputRequest() # DetectorCreationInputRequest | 

    try:
        api_response = api_instance.create_detector(detector_creation_input_request)
        print("The response of DetectorsApi->create_detector:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DetectorsApi->create_detector: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **detector_creation_input_request** | [**DetectorCreationInputRequest**](DetectorCreationInputRequest.md)|  | 

### Return type

[**Detector**](Detector.md)

### Authorization

[ApiToken](../README.md#ApiToken)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_detector**
> delete_detector(id)



Delete a detector by its ID.

### Example

* Api Key Authentication (ApiToken):
```python
import time
import os
import groundlight_openapi_client
from groundlight_openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.groundlight.ai/device-api
# See configuration.py for a list of all supported configuration parameters.
configuration = groundlight_openapi_client.Configuration(
    host = "https://api.groundlight.ai/device-api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: ApiToken
configuration.api_key['ApiToken'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiToken'] = 'Bearer'

# Enter a context with an instance of the API client
with groundlight_openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = groundlight_openapi_client.DetectorsApi(api_client)
    id = 'id_example' # str | Choose a detector by its ID.

    try:
        api_instance.delete_detector(id)
    except Exception as e:
        print("Exception when calling DetectorsApi->delete_detector: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Choose a detector by its ID. | 

### Return type

void (empty response body)

### Authorization

[ApiToken](../README.md#ApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | No response body |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_detector**
> Detector get_detector(id)



Retrieve a detector by its ID.

### Example

* Api Key Authentication (ApiToken):
```python
import time
import os
import groundlight_openapi_client
from groundlight_openapi_client.models.detector import Detector
from groundlight_openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.groundlight.ai/device-api
# See configuration.py for a list of all supported configuration parameters.
configuration = groundlight_openapi_client.Configuration(
    host = "https://api.groundlight.ai/device-api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: ApiToken
configuration.api_key['ApiToken'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiToken'] = 'Bearer'

# Enter a context with an instance of the API client
with groundlight_openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = groundlight_openapi_client.DetectorsApi(api_client)
    id = 'id_example' # str | Choose a detector by its ID.

    try:
        api_response = api_instance.get_detector(id)
        print("The response of DetectorsApi->get_detector:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DetectorsApi->get_detector: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Choose a detector by its ID. | 

### Return type

[**Detector**](Detector.md)

### Authorization

[ApiToken](../README.md#ApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_detector_evaluation**
> GetDetectorEvaluation200Response get_detector_evaluation(id)



Get Detector evaluation results. The result is null if there isn't enough ground truth data to evaluate the detector. Returns the time of the evaulation, total ground truth labels, the ml based kfold accuracies, and the system accuracies at different confidence thresholds

### Example

* Api Key Authentication (ApiToken):
```python
import time
import os
import groundlight_openapi_client
from groundlight_openapi_client.models.get_detector_evaluation200_response import GetDetectorEvaluation200Response
from groundlight_openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.groundlight.ai/device-api
# See configuration.py for a list of all supported configuration parameters.
configuration = groundlight_openapi_client.Configuration(
    host = "https://api.groundlight.ai/device-api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: ApiToken
configuration.api_key['ApiToken'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiToken'] = 'Bearer'

# Enter a context with an instance of the API client
with groundlight_openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = groundlight_openapi_client.DetectorsApi(api_client)
    id = 'id_example' # str | 

    try:
        api_response = api_instance.get_detector_evaluation(id)
        print("The response of DetectorsApi->get_detector_evaluation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DetectorsApi->get_detector_evaluation: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 

### Return type

[**GetDetectorEvaluation200Response**](GetDetectorEvaluation200Response.md)

### Authorization

[ApiToken](../README.md#ApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_detector_metrics**
> GetDetectorMetrics200Response get_detector_metrics(detector_id)



Get Detector metrics, primarily the counts of different types of labels

### Example

* Api Key Authentication (ApiToken):
```python
import time
import os
import groundlight_openapi_client
from groundlight_openapi_client.models.get_detector_metrics200_response import GetDetectorMetrics200Response
from groundlight_openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.groundlight.ai/device-api
# See configuration.py for a list of all supported configuration parameters.
configuration = groundlight_openapi_client.Configuration(
    host = "https://api.groundlight.ai/device-api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: ApiToken
configuration.api_key['ApiToken'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiToken'] = 'Bearer'

# Enter a context with an instance of the API client
with groundlight_openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = groundlight_openapi_client.DetectorsApi(api_client)
    detector_id = 'detector_id_example' # str | 

    try:
        api_response = api_instance.get_detector_metrics(detector_id)
        print("The response of DetectorsApi->get_detector_metrics:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DetectorsApi->get_detector_metrics: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **detector_id** | **str**|  | 

### Return type

[**GetDetectorMetrics200Response**](GetDetectorMetrics200Response.md)

### Authorization

[ApiToken](../README.md#ApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_detectors**
> PaginatedDetectorList list_detectors(page=page, page_size=page_size)



Retrieve a list of detectors.

### Example

* Api Key Authentication (ApiToken):
```python
import time
import os
import groundlight_openapi_client
from groundlight_openapi_client.models.paginated_detector_list import PaginatedDetectorList
from groundlight_openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.groundlight.ai/device-api
# See configuration.py for a list of all supported configuration parameters.
configuration = groundlight_openapi_client.Configuration(
    host = "https://api.groundlight.ai/device-api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: ApiToken
configuration.api_key['ApiToken'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiToken'] = 'Bearer'

# Enter a context with an instance of the API client
with groundlight_openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = groundlight_openapi_client.DetectorsApi(api_client)
    page = 56 # int | A page number within the paginated result set. (optional)
    page_size = 56 # int | Number of items to return per page. (optional)

    try:
        api_response = api_instance.list_detectors(page=page, page_size=page_size)
        print("The response of DetectorsApi->list_detectors:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DetectorsApi->list_detectors: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**| A page number within the paginated result set. | [optional] 
 **page_size** | **int**| Number of items to return per page. | [optional] 

### Return type

[**PaginatedDetectorList**](PaginatedDetectorList.md)

### Authorization

[ApiToken](../README.md#ApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_detector**
> Detector update_detector(id, patched_detector_request=patched_detector_request)



Update a detector

### Example

* Api Key Authentication (ApiToken):
```python
import time
import os
import groundlight_openapi_client
from groundlight_openapi_client.models.detector import Detector
from groundlight_openapi_client.models.patched_detector_request import PatchedDetectorRequest
from groundlight_openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.groundlight.ai/device-api
# See configuration.py for a list of all supported configuration parameters.
configuration = groundlight_openapi_client.Configuration(
    host = "https://api.groundlight.ai/device-api"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: ApiToken
configuration.api_key['ApiToken'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiToken'] = 'Bearer'

# Enter a context with an instance of the API client
with groundlight_openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = groundlight_openapi_client.DetectorsApi(api_client)
    id = 'id_example' # str | 
    patched_detector_request = groundlight_openapi_client.PatchedDetectorRequest() # PatchedDetectorRequest |  (optional)

    try:
        api_response = api_instance.update_detector(id, patched_detector_request=patched_detector_request)
        print("The response of DetectorsApi->update_detector:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DetectorsApi->update_detector: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  | 
 **patched_detector_request** | [**PatchedDetectorRequest**](PatchedDetectorRequest.md)|  | [optional] 

### Return type

[**Detector**](Detector.md)

### Authorization

[ApiToken](../README.md#ApiToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

