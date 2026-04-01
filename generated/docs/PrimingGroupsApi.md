# groundlight_openapi_client.PrimingGroupsApi

All URIs are relative to *https://api.groundlight.ai/device-api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_priming_group**](PrimingGroupsApi.md#create_priming_group) | **POST** /v1/priming-groups | 
[**delete_priming_group**](PrimingGroupsApi.md#delete_priming_group) | **DELETE** /v1/priming-groups/{id} | 
[**get_priming_group**](PrimingGroupsApi.md#get_priming_group) | **GET** /v1/priming-groups/{id} | 
[**list_priming_groups**](PrimingGroupsApi.md#list_priming_groups) | **GET** /v1/priming-groups | 


# **create_priming_group**
> PrimingGroup create_priming_group(priming_group_creation_input_request)



Create a new priming group seeded from an existing trained MLPipeline.  The cached_vizlogic_key from the source pipeline is copied as the base binary. No FK to the source pipeline is stored, so deleting the source detector does not affect this priming group.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import priming_groups_api
from groundlight_openapi_client.model.priming_group_creation_input_request import PrimingGroupCreationInputRequest
from groundlight_openapi_client.model.priming_group import PrimingGroup
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
    api_instance = priming_groups_api.PrimingGroupsApi(api_client)
    priming_group_creation_input_request = PrimingGroupCreationInputRequest(
        name="name_example",
        source_ml_pipeline_id="source_ml_pipeline_id_example",
        canonical_query="canonical_query_example",
        disable_shadow_pipelines=False,
    ) # PrimingGroupCreationInputRequest | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.create_priming_group(priming_group_creation_input_request)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling PrimingGroupsApi->create_priming_group: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **priming_group_creation_input_request** | [**PrimingGroupCreationInputRequest**](PrimingGroupCreationInputRequest.md)|  |

### Return type

[**PrimingGroup**](PrimingGroup.md)

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

# **delete_priming_group**
> delete_priming_group(id)



Delete a priming group. Only the owning user's account may delete it.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import priming_groups_api
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
    api_instance = priming_groups_api.PrimingGroupsApi(api_client)
    id = "id_example" # str | 

    # example passing only required values which don't have defaults set
    try:
        api_instance.delete_priming_group(id)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling PrimingGroupsApi->delete_priming_group: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  |

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

# **get_priming_group**
> PrimingGroup get_priming_group(id)



Retrieve a priming group by its ID.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import priming_groups_api
from groundlight_openapi_client.model.priming_group import PrimingGroup
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
    api_instance = priming_groups_api.PrimingGroupsApi(api_client)
    id = "id_example" # str | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.get_priming_group(id)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling PrimingGroupsApi->get_priming_group: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**|  |

### Return type

[**PrimingGroup**](PrimingGroup.md)

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

# **list_priming_groups**
> PaginatedPrimingGroupList list_priming_groups()



List all priming groups owned by the authenticated user.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import priming_groups_api
from groundlight_openapi_client.model.paginated_priming_group_list import PaginatedPrimingGroupList
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
    api_instance = priming_groups_api.PrimingGroupsApi(api_client)
    ordering = "ordering_example" # str | Which field to use when ordering the results. (optional)
    page = 1 # int | A page number within the paginated result set. (optional)
    page_size = 1 # int | Number of results to return per page. (optional)
    search = "search_example" # str | A search term. (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.list_priming_groups(ordering=ordering, page=page, page_size=page_size, search=search)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling PrimingGroupsApi->list_priming_groups: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ordering** | **str**| Which field to use when ordering the results. | [optional]
 **page** | **int**| A page number within the paginated result set. | [optional]
 **page_size** | **int**| Number of results to return per page. | [optional]
 **search** | **str**| A search term. | [optional]

### Return type

[**PaginatedPrimingGroupList**](PaginatedPrimingGroupList.md)

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

