# groundlight_openapi_client.ApiTokensApi

All URIs are relative to *https://api.groundlight.ai/device-api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_api_token**](ApiTokensApi.md#create_api_token) | **POST** /v1/api-tokens | 
[**delete_api_token**](ApiTokensApi.md#delete_api_token) | **DELETE** /v1/api-tokens/{name} | 
[**get_api_token_by_snippet**](ApiTokensApi.md#get_api_token_by_snippet) | **GET** /v1/api-tokens/by-snippet/{snippet} | 
[**list_api_tokens**](ApiTokensApi.md#list_api_tokens) | **GET** /v1/api-tokens | 


# **create_api_token**
> ApiTokenCreateResponse create_api_token(api_token_request)



Create a new API token, returning the raw_key exactly once in the response.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import api_tokens_api
from groundlight_openapi_client.model.api_token_request import ApiTokenRequest
from groundlight_openapi_client.model.api_token_create_response import ApiTokenCreateResponse
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
    api_instance = api_tokens_api.ApiTokensApi(api_client)
    api_token_request = ApiTokenRequest(
        name="name_example",
        expires_at=dateutil_parser('1970-01-01T00:00:00.00Z'),
    ) # ApiTokenRequest | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.create_api_token(api_token_request)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling ApiTokensApi->create_api_token: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_token_request** | [**ApiTokenRequest**](ApiTokenRequest.md)|  |

### Return type

[**ApiTokenCreateResponse**](ApiTokenCreateResponse.md)

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

# **delete_api_token**
> delete_api_token(name)



Delete (revoke) an API token by name. The token must belong to the authenticated user.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import api_tokens_api
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
    api_instance = api_tokens_api.ApiTokensApi(api_client)
    name = "name_example" # str | 

    # example passing only required values which don't have defaults set
    try:
        api_instance.delete_api_token(name)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling ApiTokensApi->delete_api_token: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  |

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

# **get_api_token_by_snippet**
> ApiToken get_api_token_by_snippet(snippet)



Retrieve a single API token by its raw_key_snippet. Returns metadata only; the raw key is never retrievable after creation.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import api_tokens_api
from groundlight_openapi_client.model.api_token import ApiToken
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
    api_instance = api_tokens_api.ApiTokensApi(api_client)
    snippet = "snippet_example" # str | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.get_api_token_by_snippet(snippet)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling ApiTokensApi->get_api_token_by_snippet: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **snippet** | **str**|  |

### Return type

[**ApiToken**](ApiToken.md)

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

# **list_api_tokens**
> PaginatedApiTokenList list_api_tokens()



List all API tokens for the authenticated user. Returns metadata only; raw keys are never retrievable after creation.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import api_tokens_api
from groundlight_openapi_client.model.paginated_api_token_list import PaginatedApiTokenList
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
    api_instance = api_tokens_api.ApiTokensApi(api_client)
    page = 1 # int | A page number within the paginated result set. (optional)
    page_size = 1 # int | Number of results to return per page. (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.list_api_tokens(page=page, page_size=page_size)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling ApiTokensApi->list_api_tokens: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**| A page number within the paginated result set. | [optional]
 **page_size** | **int**| Number of results to return per page. | [optional]

### Return type

[**PaginatedApiTokenList**](PaginatedApiTokenList.md)

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

