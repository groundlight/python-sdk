# groundlight_openapi_client.EdgeApi

All URIs are relative to *https://api.groundlight.ai/device-api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**edge_report_metrics_create**](EdgeApi.md#edge_report_metrics_create) | **POST** /v1/edge/report-metrics | 
[**get_gll_model_info**](EdgeApi.md#get_gll_model_info) | **GET** /v1/edge/model-info/{detector_id}/ | 
[**get_gll_pipeline**](EdgeApi.md#get_gll_pipeline) | **GET** /v1/edge/gll-pipeline/{detector_id}/ | 
[**get_gll_tensor_rt_engine_build**](EdgeApi.md#get_gll_tensor_rt_engine_build) | **GET** /v1/edge/gll-engine/{detector_id}/ | 
[**get_model_urls**](EdgeApi.md#get_model_urls) | **GET** /v1/edge/fetch-model-urls/{detector_id}/ | 
[**initiate_gll_pipeline_build**](EdgeApi.md#initiate_gll_pipeline_build) | **POST** /v1/edge/gll-pipeline/{detector_id}/ | 
[**initiate_gll_tensor_rt_engine_build**](EdgeApi.md#initiate_gll_tensor_rt_engine_build) | **POST** /v1/edge/gll-engine/{detector_id}/ | 


# **edge_report_metrics_create**
> edge_report_metrics_create()



Edge server periodically calls this to report metrics.  POST body will have JSON data that we log.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import edge_api
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
    api_instance = edge_api.EdgeApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_instance.edge_report_metrics_create()
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling EdgeApi->edge_report_metrics_create: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

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
**200** | No response body |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_gll_model_info**
> GLLModelInfo get_gll_model_info(detector_id)



Lightweight model-info pointer for `Pipeline.has_update_available()`.  Returns the current `model_binary_id`, `oodd_model_binary_id`, `mode`, and `updated_at` for a GLL-compatible detector. NO S3 calls, NO pre-signed URLs - one DB read per request, with a short client-side Cache-Control so polling clients can't hammer janzu.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import edge_api
from groundlight_openapi_client.model.gll_model_info import GLLModelInfo
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
    api_instance = edge_api.EdgeApi(api_client)
    detector_id = "detector_id_example" # str | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.get_gll_model_info(detector_id)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling EdgeApi->get_gll_model_info: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **detector_id** | **str**|  |

### Return type

[**GLLModelInfo**](GLLModelInfo.md)

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

# **get_gll_pipeline**
> GLLPipelineInfo get_gll_pipeline(detector_id)



Look up current build state without dispatching work.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import edge_api
from groundlight_openapi_client.model.gll_pipeline_info import GLLPipelineInfo
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
    api_instance = edge_api.EdgeApi(api_client)
    detector_id = "detector_id_example" # str | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.get_gll_pipeline(detector_id)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling EdgeApi->get_gll_pipeline: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **detector_id** | **str**|  |

### Return type

[**GLLPipelineInfo**](GLLPipelineInfo.md)

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

# **get_gll_tensor_rt_engine_build**
> GLLEngineInfo get_gll_tensor_rt_engine_build(detector_id)



Get pre-signed URL + sidecar for a TensorRT engine.  Query params:     cc: Compute capability (e.g., \"8.9\" for Ada/L4, \"7.5\" for Turing/T4)     precision: Precision mode (default: \"fp16\")     batch_size: Batch size (default: 1)     trt_version: TensorRT version major.minor[.patch...] (default: server's installed TRT version)  Returns:     200: Engine URL + sidecar metadata     400: Invalid params     403: Edge model download not enabled     404: Detector or matching engine not found

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import edge_api
from groundlight_openapi_client.model.gll_engine_info import GLLEngineInfo
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
    api_instance = edge_api.EdgeApi(api_client)
    detector_id = "detector_id_example" # str | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.get_gll_tensor_rt_engine_build(detector_id)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling EdgeApi->get_gll_tensor_rt_engine_build: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **detector_id** | **str**|  |

### Return type

[**GLLEngineInfo**](GLLEngineInfo.md)

### Authorization

[ApiToken](../README.md#ApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**404** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_model_urls**
> EdgeModelInfo get_model_urls(detector_id)



Gets time limited pre-authenticated URLs to download a detector's edge model and oodd model.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import edge_api
from groundlight_openapi_client.model.edge_model_info import EdgeModelInfo
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
    api_instance = edge_api.EdgeApi(api_client)
    detector_id = "detector_id_example" # str | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.get_model_urls(detector_id)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling EdgeApi->get_model_urls: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **detector_id** | **str**|  |

### Return type

[**EdgeModelInfo**](EdgeModelInfo.md)

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

# **initiate_gll_pipeline_build**
> GLLPipelineInfo initiate_gll_pipeline_build(detector_id)



Initiate or deduplicate an ONNX export.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import edge_api
from groundlight_openapi_client.model.gll_pipeline_info import GLLPipelineInfo
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
    api_instance = edge_api.EdgeApi(api_client)
    detector_id = "detector_id_example" # str | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.initiate_gll_pipeline_build(detector_id)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling EdgeApi->initiate_gll_pipeline_build: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **detector_id** | **str**|  |

### Return type

[**GLLPipelineInfo**](GLLPipelineInfo.md)

### Authorization

[ApiToken](../README.md#ApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**202** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **initiate_gll_tensor_rt_engine_build**
> GLLEngineInfo initiate_gll_tensor_rt_engine_build(detector_id, gll_engine_info_request)



Request TensorRT engine build.  Query params or body:     compute_capability: Compute capability (default: configured builder GPU)     precision: Precision mode (default: \"fp16\")     batch_size: Batch size (default: 1)     trt_version: TensorRT version (default: server's installed TRT version)  Returns:     200: Already built     202: Build requested     400: Invalid parameters     403: Not authorized     409: Requested TRT version doesn't match build worker

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import edge_api
from groundlight_openapi_client.model.gll_engine_info_request import GLLEngineInfoRequest
from groundlight_openapi_client.model.gll_engine_info import GLLEngineInfo
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
    api_instance = edge_api.EdgeApi(api_client)
    detector_id = "detector_id_example" # str | 
    gll_engine_info_request = GLLEngineInfoRequest(
        build_key="build_key_example",
        status=Status638Enum("not_requested"),
        stale_from_status=StaleFromStatusEnum("queued"),
        generation=1,
        task_id="task_id_example",
        attempt_count=1,
        engine_url="engine_url_example",
        engine_s3_key="engine_s3_key_example",
        metadata=None,
        metadata_s3_key="metadata_s3_key_example",
        model_binary_id="model_binary_id_example",
        compute_capability="compute_capability_example",
        precision="precision_example",
        batch_size=1,
        trt_version="trt_version_example",
        workspace_bytes=1,
        engine_contract_version="engine_contract_version_example",
        metadata_format_version="metadata_format_version_example",
        error_code="error_code_example",
        error_message="error_message_example",
        updated_at=dateutil_parser('1970-01-01T00:00:00.00Z'),
        expires_at=dateutil_parser('1970-01-01T00:00:00.00Z'),
    ) # GLLEngineInfoRequest | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.initiate_gll_tensor_rt_engine_build(detector_id, gll_engine_info_request)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling EdgeApi->initiate_gll_tensor_rt_engine_build: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **detector_id** | **str**|  |
 **gll_engine_info_request** | [**GLLEngineInfoRequest**](GLLEngineInfoRequest.md)|  |

### Return type

[**GLLEngineInfo**](GLLEngineInfo.md)

### Authorization

[ApiToken](../README.md#ApiToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**202** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

