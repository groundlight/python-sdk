# groundlight_openapi_client.UserApi

All URIs are relative to *https://api.groundlight.ai/device-api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**who_am_i**](UserApi.md#who_am_i) | **GET** /v1/me | 


# **who_am_i**
> WhoAmI200Response who_am_i()

Retrieve the current user.

### Example

* Api Key Authentication (ApiToken):

```python
import groundlight_openapi_client
from groundlight_openapi_client.models.who_am_i200_response import WhoAmI200Response
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
    api_instance = groundlight_openapi_client.UserApi(api_client)

    try:
        api_response = api_instance.who_am_i()
        print("The response of UserApi->who_am_i:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UserApi->who_am_i: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**WhoAmI200Response**](WhoAmI200Response.md)

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

