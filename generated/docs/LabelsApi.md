# groundlight_openapi_client.LabelsApi

All URIs are relative to *https://api.groundlight.ai/device-api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_label**](LabelsApi.md#create_label) | **POST** /v1/labels | 


# **create_label**
> LabelValue create_label(label_value_request)



Create a new LabelValue and attach it to an image query. This will trigger asynchronous fine-tuner model training.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import labels_api
from groundlight_openapi_client.model.label_value import LabelValue
from groundlight_openapi_client.model.label_value_request import LabelValueRequest
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
    api_instance = labels_api.LabelsApi(api_client)
    label_value_request = LabelValueRequest(
        label="label_example",
        posicheck_id="posicheck_id_example",
        value=3.14,
        feedback_text="feedback_text_example",
        rois=None,
        flag_archived=True,
        review_reason=None,
    ) # LabelValueRequest | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.create_label(label_value_request)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling LabelsApi->create_label: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **label_value_request** | [**LabelValueRequest**](LabelValueRequest.md)|  |

### Return type

[**LabelValue**](LabelValue.md)

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

