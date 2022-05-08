# openapi_client.ImageQueriesApi

All URIs are relative to *https://device.positronix.ai/device-api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_image_query**](ImageQueriesApi.md#get_image_query) | **GET** /v1/image-queries/{id} | 
[**list_image_queries**](ImageQueriesApi.md#list_image_queries) | **GET** /v1/image-queries | 
[**submit_image_query**](ImageQueriesApi.md#submit_image_query) | **POST** /v1/image-queries | 


# **get_image_query**
> ImageQuery get_image_query(id)



Retrieve an image-query by its ID.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import openapi_client
from openapi_client.api import image_queries_api
from openapi_client.model.image_query import ImageQuery
from pprint import pprint
# Defining the host is optional and defaults to https://device.positronix.ai/device-api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://device.positronix.ai/device-api"
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
    api_instance = image_queries_api.ImageQueriesApi(api_client)
    id = "id_example" # str | Choose an image query by its ID.

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.get_image_query(id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ImageQueriesApi->get_image_query: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Choose an image query by its ID. |

### Return type

[**ImageQuery**](ImageQuery.md)

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

# **list_image_queries**
> PaginatedImageQueryList list_image_queries()



Retrieve a list of image-queries.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import openapi_client
from openapi_client.api import image_queries_api
from openapi_client.model.paginated_image_query_list import PaginatedImageQueryList
from pprint import pprint
# Defining the host is optional and defaults to https://device.positronix.ai/device-api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://device.positronix.ai/device-api"
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
    api_instance = image_queries_api.ImageQueriesApi(api_client)
    page = 1 # int | A page number within the paginated result set. (optional)
    page_size = 1 # int | Number of results to return per page. (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.list_image_queries(page=page, page_size=page_size)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ImageQueriesApi->list_image_queries: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**| A page number within the paginated result set. | [optional]
 **page_size** | **int**| Number of results to return per page. | [optional]

### Return type

[**PaginatedImageQueryList**](PaginatedImageQueryList.md)

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

# **submit_image_query**
> ImageQuery submit_image_query(detector_id)



 Submit an image query against a detector.  You must use `\"Content-Type: image/jpeg\"` for the image data. For example:  ```Bash $ curl https://api.groundlight.ai/v1/image-queries?detector_id=det_abc123 \\     --header \"Content-Type: image/jpeg\" \\     --data-binary @path/to/filename.jpeg ```  

### Example

* Api Key Authentication (ApiToken):

```python
import time
import openapi_client
from openapi_client.api import image_queries_api
from openapi_client.model.image_query import ImageQuery
from pprint import pprint
# Defining the host is optional and defaults to https://device.positronix.ai/device-api
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://device.positronix.ai/device-api"
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
    api_instance = image_queries_api.ImageQueriesApi(api_client)
    detector_id = "detector_id_example" # str | Choose a detector by its ID.
    image_query = ImageQuery(
    ) # ImageQuery |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.submit_image_query(detector_id)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ImageQueriesApi->submit_image_query: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.submit_image_query(detector_id, image_query=image_query)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ImageQueriesApi->submit_image_query: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **detector_id** | **str**| Choose a detector by its ID. |
 **image_query** | [**ImageQuery**](ImageQuery.md)|  | [optional]

### Return type

[**ImageQuery**](ImageQuery.md)

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

