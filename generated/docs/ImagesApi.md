# openapi_client.ImagesApi

All URIs are relative to *https://api.groundlight.ai/device-api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_image**](ImagesApi.md#get_image) | **GET** /v1/image-queries/{id}/image | 


# **get_image**
> file_type get_image(id)



Retrieve an image by its image query id.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import openapi_client
from openapi_client.api import images_api
from pprint import pprint
# Defining the host is optional and defaults to https://api.groundlight.ai/device-api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
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
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = images_api.ImagesApi(api_client)
    id = "id_example" # str | Choose an image by its image query id.

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.get_image(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ImagesApi->get_image: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Choose an image by its image query id. |

### Return type

**file_type**

### Authorization

[ApiToken](../README.md#ApiToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: image/jpeg


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

