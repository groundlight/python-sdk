# groundlight_openapi_client.VlmVerificationsApi

All URIs are relative to *https://api.groundlight.ai/device-api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**submit_vlm_verification**](VlmVerificationsApi.md#submit_vlm_verification) | **POST** /v1/vlm-verifications | 


# **submit_vlm_verification**
> VlmVerification submit_vlm_verification(media, query)



 Submit one or more images for VLM-based alert verification.  Send everything as `multipart/form-data`: one to eight `media` parts, plus a `query` field and an optional `model_id` field.  The `query` describes what each image is and what to look for — the server makes no assumptions about the images' meaning. Images are presented to the model labeled `Image 1`, `Image 2`, ... in upload order, so the query can reference them (e.g. \"Image 1 is the full frame; image 2 is the cropped ROI ...\").  (Video parts are planned but not yet supported and are rejected.)  Requires `ENABLE_BEDROCK_VLM_ACCESS` (enabled for Standard_Internal and SciDuck accounts) and accepted terms of service.  ```bash curl https://api.groundlight.ai/device-api/v1/vlm-verifications \\     -F \"media=@full_frame.jpg;type=image/jpeg\" \\     -F \"media=@roi.jpg;type=image/jpeg\" \\     -F \"query=Image 1 is the full camera frame; image 2 is the cropped region a detector flagged. Is there really a fire?\" \\     -F \"model_id=gpt-5.4\" ``` 

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import vlm_verifications_api
from groundlight_openapi_client.model.vlm_verification import VlmVerification
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
    api_instance = vlm_verifications_api.VlmVerificationsApi(api_client)
    media = [
        open('/path/to/file', 'rb'),
    ] # [file_type] | One or more images (common formats: JPEG, PNG, WEBP). Video is not yet supported.
    query = "query_example" # str | Natural-language prompt describing the media and what to verify.
    model_id = "model_id_example" # str | Friendly model alias (e.g. 'gpt-5.4', 'claude-sonnet-4.5'). Defaults to the server default. (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.submit_vlm_verification(media, query)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling VlmVerificationsApi->submit_vlm_verification: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.submit_vlm_verification(media, query, model_id=model_id)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling VlmVerificationsApi->submit_vlm_verification: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **media** | **[file_type]**| One or more images (common formats: JPEG, PNG, WEBP). Video is not yet supported. |
 **query** | **str**| Natural-language prompt describing the media and what to verify. |
 **model_id** | **str**| Friendly model alias (e.g. &#39;gpt-5.4&#39;, &#39;claude-sonnet-4.5&#39;). Defaults to the server default. | [optional]

### Return type

[**VlmVerification**](VlmVerification.md)

### Authorization

[ApiToken](../README.md#ApiToken)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

