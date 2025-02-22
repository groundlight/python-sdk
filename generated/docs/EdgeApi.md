# groundlight_openapi_client.EdgeApi

All URIs are relative to *https://api.groundlight.ai/device-api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_model_urls**](EdgeApi.md#get_model_urls) | **GET** /v1/edge/fetch-model-urls/{detector_id}/ | 


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

