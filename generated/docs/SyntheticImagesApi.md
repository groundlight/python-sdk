# groundlight_openapi_client.SyntheticImagesApi

All URIs are relative to *https://api.groundlight.ai/device-api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**generate_synthetic_image**](SyntheticImagesApi.md#generate_synthetic_image) | **POST** /v1/synthetic-images | 


# **generate_synthetic_image**
> SyntheticImage generate_synthetic_image(lens_type)



 Submit an image for synthetic augmentation and get the edited image back with ground-truth annotations, in one call.  Send the raw image bytes as the entire request body with a `Content-Type` of `image/jpeg` or `image/png`; `lens_type` and `lens_config` go in the query string. The lens selects what kind of event to synthesize.  Top-level `label` is the lens-level binary event label (`YES`/`NO`) for the generated image, and can be forwarded to `POST /v1/labels` alongside `rois` without translation. `rois` lists every detected object, including ones already present in the frame; `added_roi_index` points at the one this request inserted.  Nothing is persisted: the generated image is returned inline and never stored.  Requires `ENABLE_SYNTHETIC_IMAGE_ACCESS` and accepted terms of service.  ```bash curl \"https://api.groundlight.ai/device-api/v1/synthetic-images?lens_type=fence_climbing\" \\     -H \"Content-Type: image/jpeg\" \\     --data-binary @camera_frame.jpg ``` 

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import synthetic_images_api
from groundlight_openapi_client.model.synthetic_image import SyntheticImage
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
    api_instance = synthetic_images_api.SyntheticImagesApi(api_client)
    lens_type = "lens_type_example" # str | Which lens to generate the image for, e.g. `fence_climbing`.
    lens_config = "lens_config_example" # str | Lens-specific settings as a base64 url-safe encoded JSON object (up to 1KiB). (optional)
    body = open('/path/to/file', 'rb') # file_type |  (optional)

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.generate_synthetic_image(lens_type)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling SyntheticImagesApi->generate_synthetic_image: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.generate_synthetic_image(lens_type, lens_config=lens_config, body=body)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling SyntheticImagesApi->generate_synthetic_image: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lens_type** | **str**| Which lens to generate the image for, e.g. &#x60;fence_climbing&#x60;. |
 **lens_config** | **str**| Lens-specific settings as a base64 url-safe encoded JSON object (up to 1KiB). | [optional]
 **body** | **file_type**|  | [optional]

### Return type

[**SyntheticImage**](SyntheticImage.md)

### Authorization

[ApiToken](../README.md#ApiToken)

### HTTP request headers

 - **Content-Type**: image/jpeg, image/jpg, image/png
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

