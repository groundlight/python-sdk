# openapi_client.ImageQueriesApi

All URIs are relative to *https://device.positronix.ai/device-api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**retrieve_an_image_query**](ImageQueriesApi.md#retrieve_an_image_query) | **GET** /v1/image-queries/{id} | 
[**retrieve_image_queries**](ImageQueriesApi.md#retrieve_image_queries) | **GET** /v1/image-queries | 
[**submit_an_image_query**](ImageQueriesApi.md#submit_an_image_query) | **POST** /v1/image-queries | 

# **retrieve_an_image_query**
> ImageQuery retrieve_an_image_query(id)



Retrieve an image-query by its ID.

### Example

* Api Key Authentication (ApiToken):
```python
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

    # example passing only required values which don't have defaults set
    path_params = {
        'id': "id_example",
    }
    try:
        api_response = api_instance.retrieve_an_image_query(
            path_params=path_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ImageQueriesApi->retrieve_an_image_query: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
path_params | RequestPathParams | |
accept_content_types | typing.Tuple[str] | default is ('application/json', ) | Tells the server the content type(s) that are accepted by the client
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### path_params
#### RequestPathParams

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
id | IdSchema | | 

#### IdSchema

Type | Description | Notes
------------- | ------------- | -------------
**str** |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | ApiResponseFor200 |  

#### ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

#### SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**ImageQuery**](ImageQuery.md) |  | 



[**ImageQuery**](ImageQuery.md)

### Authorization

[ApiToken](../README.md#ApiToken)

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **retrieve_image_queries**
> PaginatedImageQueryList retrieve_image_queries()



Retrieve a list of image-queries.

### Example

* Api Key Authentication (ApiToken):
```python
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

    # example passing only optional values
    query_params = {
        'page': 1,
        'page_size': 1,
    }
    try:
        api_response = api_instance.retrieve_image_queries(
            query_params=query_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ImageQueriesApi->retrieve_image_queries: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
query_params | RequestQueryParams | |
accept_content_types | typing.Tuple[str] | default is ('application/json', ) | Tells the server the content type(s) that are accepted by the client
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### query_params
#### RequestQueryParams

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
page | PageSchema | | optional
page_size | PageSizeSchema | | optional


#### PageSchema

Type | Description | Notes
------------- | ------------- | -------------
**int** |  | 

#### PageSizeSchema

Type | Description | Notes
------------- | ------------- | -------------
**int** |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
200 | ApiResponseFor200 |  

#### ApiResponseFor200
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor200ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

#### SchemaFor200ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**PaginatedImageQueryList**](PaginatedImageQueryList.md) |  | 



[**PaginatedImageQueryList**](PaginatedImageQueryList.md)

### Authorization

[ApiToken](../README.md#ApiToken)

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **submit_an_image_query**
> ImageQuery submit_an_image_query(detector_id)



 Submit an image query against a detector.  You must use `\"Content-Type: image/jpeg\"` for the image data. For example:  ```Bash $ curl https://api.groundlight.ai/v1/image-queries?detector_id=det_abc123 \\     --header \"Content-Type: image/jpeg\" \\     --data-binary @path/to/filename.jpeg ```  

### Example

* Api Key Authentication (ApiToken):
```python
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

    # example passing only required values which don't have defaults set
    query_params = {
        'detector_id': "detector_id_example",
    }
    try:
        api_response = api_instance.submit_an_image_query(
            query_params=query_params,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ImageQueriesApi->submit_an_image_query: %s\n" % e)

    # example passing only optional values
    query_params = {
        'detector_id': "detector_id_example",
    }
    body = ImageQuery(
        id="id_example",
        type=,
        created_at=isoparse('1970-01-01T00:00:00.00Z'),
        query="query_example",
        detector_id="detector_id_example",
        result_type=,
        result=,
    )
    try:
        api_response = api_instance.submit_an_image_query(
            query_params=query_params,
            body=body,
        )
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ImageQueriesApi->submit_an_image_query: %s\n" % e)
```
### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
body | typing.Union[SchemaForRequestBodyApplicationJson, SchemaForRequestBodyApplicationXWwwFormUrlencoded, SchemaForRequestBodyMultipartFormData, Unset] | optional, default is unset |
query_params | RequestQueryParams | |
content_type | str | optional, default is 'application/json' | Selects the schema and serialization of the request body
accept_content_types | typing.Tuple[str] | default is ('application/json', ) | Tells the server the content type(s) that are accepted by the client
stream | bool | default is False | if True then the response.content will be streamed and loaded from a file like object. When downloading a file, set this to True to force the code to deserialize the content to a FileSchema file
timeout | typing.Optional[typing.Union[int, typing.Tuple]] | default is None | the timeout used by the rest client
skip_deserialization | bool | default is False | when True, headers and body will be unset and an instance of api_client.ApiResponseWithoutDeserialization will be returned

### body

#### SchemaForRequestBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**ImageQuery**](ImageQuery.md) |  | 


#### SchemaForRequestBodyApplicationXWwwFormUrlencoded
Type | Description  | Notes
------------- | ------------- | -------------
[**ImageQuery**](ImageQuery.md) |  | 


#### SchemaForRequestBodyMultipartFormData
Type | Description  | Notes
------------- | ------------- | -------------
[**ImageQuery**](ImageQuery.md) |  | 


### query_params
#### RequestQueryParams

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
detector_id | DetectorIdSchema | | 


#### DetectorIdSchema

Type | Description | Notes
------------- | ------------- | -------------
**str** |  | 

### Return Types, Responses

Code | Class | Description
------------- | ------------- | -------------
n/a | api_client.ApiResponseWithoutDeserialization | When skip_deserialization is True this response is returned
201 | ApiResponseFor201 |  

#### ApiResponseFor201
Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
response | urllib3.HTTPResponse | Raw response |
body | typing.Union[SchemaFor201ResponseBodyApplicationJson, ] |  |
headers | Unset | headers were not defined |

#### SchemaFor201ResponseBodyApplicationJson
Type | Description  | Notes
------------- | ------------- | -------------
[**ImageQuery**](ImageQuery.md) |  | 



[**ImageQuery**](ImageQuery.md)

### Authorization

[ApiToken](../README.md#ApiToken)

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

