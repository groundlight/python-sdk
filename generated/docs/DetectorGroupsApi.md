# groundlight_openapi_client.DetectorGroupsApi

All URIs are relative to *https://api.groundlight.ai/device-api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_detector_group**](DetectorGroupsApi.md#create_detector_group) | **POST** /v1/detector-groups | 
[**get_detector_groups**](DetectorGroupsApi.md#get_detector_groups) | **GET** /v1/detector-groups | 


# **create_detector_group**
> DetectorGroup create_detector_group(detector_group_request)

Create a new detector group

POST data:
  Required:
    - name (str) - name of the predictor set

### Example

* Api Key Authentication (ApiToken):

```python
import groundlight_openapi_client
from groundlight_openapi_client.models.detector_group import DetectorGroup
from groundlight_openapi_client.models.detector_group_request import DetectorGroupRequest
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
    api_instance = groundlight_openapi_client.DetectorGroupsApi(api_client)
    detector_group_request = groundlight_openapi_client.DetectorGroupRequest() # DetectorGroupRequest | 

    try:
        api_response = api_instance.create_detector_group(detector_group_request)
        print("The response of DetectorGroupsApi->create_detector_group:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DetectorGroupsApi->create_detector_group: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **detector_group_request** | [**DetectorGroupRequest**](DetectorGroupRequest.md)|  | 

### Return type

[**DetectorGroup**](DetectorGroup.md)

### Authorization

[ApiToken](../README.md#ApiToken)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_detector_groups**
> List[DetectorGroup] get_detector_groups()

List all detector groups

### Example

* Api Key Authentication (ApiToken):

```python
import groundlight_openapi_client
from groundlight_openapi_client.models.detector_group import DetectorGroup
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
    api_instance = groundlight_openapi_client.DetectorGroupsApi(api_client)

    try:
        api_response = api_instance.get_detector_groups()
        print("The response of DetectorGroupsApi->get_detector_groups:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DetectorGroupsApi->get_detector_groups: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[DetectorGroup]**](DetectorGroup.md)

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

