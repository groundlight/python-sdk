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
import groundlight_openapi_client
from groundlight_openapi_client.api import detectors_api
from groundlight_openapi_client.model.detector_creation_input_request import DetectorCreationInputRequest
from groundlight_openapi_client.model.detector import Detector
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
configuration.api_key['ApiToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiToken'] = 'Bearer'

# Enter a context with an instance of the API client
with groundlight_openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = detectors_api.DetectorsApi(api_client)
    detector_creation_input_request = DetectorCreationInputRequest(
        name="name_example",
        query="query_example",
        group_name="group_name_example",
        confidence_threshold=0.9,
        patience_time=30.0,
        pipeline_config="pipeline_config_example",
        metadata="metadata_example",
        mode=None,
        mode_configuration=None,
    ) # DetectorCreationInputRequest | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.create_detector(detector_creation_input_request)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
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
import groundlight_openapi_client
from groundlight_openapi_client.api import detectors_api
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
configuration.api_key['ApiToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiToken'] = 'Bearer'

# Enter a context with an instance of the API client
with groundlight_openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = detectors_api.DetectorsApi(api_client)
    id = "id_example" # str | Choose a detector by its ID.

    # example passing only required values which don't have defaults set
    try:
        api_instance.delete_detector(id)
    except groundlight_openapi_client.ApiException as e:
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
import groundlight_openapi_client
from groundlight_openapi_client.api import detectors_api
from groundlight_openapi_client.model.detector import Detector
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
configuration.api_key['ApiToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiToken'] = 'Bearer'

# Enter a context with an instance of the API client
with groundlight_openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = detectors_api.DetectorsApi(api_client)
    id = "id_example" # str | Choose a detector by its ID.

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.get_detector(id)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
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
> InlineResponse2001 get_detector_evaluation(id)



Get Detector evaluation results. The result is null if there isn't enough ground truth data to evaluate the detector. Returns the time of the evaulation, total ground truth labels, the ml based kfold accuracies, and the system accuracies at different confidence thresholds

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import detectors_api
from groundlight_openapi_client.model.inline_response2001 import InlineResponse2001
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
configuration.api_key['ApiToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiToken'] = 'Bearer'

# Enter a context with an instance of the API client
with groundlight_openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = detectors_api.DetectorsApi(api_client)
    id = "id_example" # str | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.get_detector_evaluation(id)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling DetectorsApi->get_detector_evaluation: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  |

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

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
> InlineResponse200 get_detector_metrics(detector_id)



Get Detector metrics, primarily the counts of different types of labels

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import detectors_api
from groundlight_openapi_client.model.inline_response200 import InlineResponse200
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
configuration.api_key['ApiToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiToken'] = 'Bearer'

# Enter a context with an instance of the API client
with groundlight_openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = detectors_api.DetectorsApi(api_client)
    detector_id = "detector_id_example" # str | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.get_detector_metrics(detector_id)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling DetectorsApi->get_detector_metrics: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **detector_id** | **str**|  |

### Return type

[**InlineResponse200**](InlineResponse200.md)

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
> PaginatedDetectorList list_detectors()



Retrieve a list of detectors.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import detectors_api
from groundlight_openapi_client.model.paginated_detector_list import PaginatedDetectorList
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
configuration.api_key['ApiToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiToken'] = 'Bearer'

# Enter a context with an instance of the API client
with groundlight_openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = detectors_api.DetectorsApi(api_client)
    page = 1 # int | A page number within the paginated result set. (optional)
    page_size = 1 # int | Number of items to return per page. (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.list_detectors(page=page, page_size=page_size)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
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
> Detector update_detector(id)



Update a detector

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import detectors_api
from groundlight_openapi_client.model.detector import Detector
from groundlight_openapi_client.model.patched_detector_request import PatchedDetectorRequest
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
configuration.api_key['ApiToken'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiToken'] = 'Bearer'

# Enter a context with an instance of the API client
with groundlight_openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = detectors_api.DetectorsApi(api_client)
    id = "id_example" # str | 
    patched_detector_request = PatchedDetectorRequest(
        name="name_example",
        confidence_threshold=0.9,
        patience_time=30.0,
        status=None,
        escalation_type=None,
    ) # PatchedDetectorRequest |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.update_detector(id)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling DetectorsApi->update_detector: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.update_detector(id, patched_detector_request=patched_detector_request)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
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

