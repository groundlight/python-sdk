# groundlight_openapi_client.AlertsApi

All URIs are relative to *https://api.groundlight.ai/device-api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_alert**](AlertsApi.md#create_alert) | **POST** /v1/alerts | 
[**create_alert_verdict**](AlertsApi.md#create_alert_verdict) | **POST** /v1/alerts/{alert_id}/verdicts | 


# **create_alert**
> Alert create_alert(alert_creation_input_request)



Create an alert, identified by your own unique ID (a UUID).  Returns 201 when the alert is created. Sending the same ID with the same fields again returns the existing alert with 200, so retries are safe. Sending the same ID with different fields returns 409.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import alerts_api
from groundlight_openapi_client.model.alert import Alert
from groundlight_openapi_client.model.alert_creation_input_request import AlertCreationInputRequest
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
    api_instance = alerts_api.AlertsApi(api_client)
    alert_creation_input_request = AlertCreationInputRequest(
        id="id_example",
        triggered_at=dateutil_parser('1970-01-01T00:00:00.00Z'),
        image_query_count=1,
        lens_id="lens_id_example",
        camera_id="camera_id_example",
        device_id="device_id_example",
    ) # AlertCreationInputRequest | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.create_alert(alert_creation_input_request)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling AlertsApi->create_alert: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **alert_creation_input_request** | [**AlertCreationInputRequest**](AlertCreationInputRequest.md)|  |

### Return type

[**Alert**](Alert.md)

### Authorization

[ApiToken](../README.md#ApiToken)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_alert_verdict**
> Verdict create_alert_verdict(alert_id, verdict_creation_input_request)



Add a verdict to the alert with your ID `alert_id`. An alert keeps every verdict it gets.  The verdict may arrive before the alert itself is created; it is kept, and the alert is filled in when it is created.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import alerts_api
from groundlight_openapi_client.model.verdict import Verdict
from groundlight_openapi_client.model.verdict_creation_input_request import VerdictCreationInputRequest
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
    api_instance = alerts_api.AlertsApi(api_client)
    alert_id = "alert_id_example" # str | 
    verdict_creation_input_request = VerdictCreationInputRequest(
        source=None,
        verdict=AlertVerdictEnum("FALSE_ALARM"),
        rationale="rationale_example",
        decided_at=dateutil_parser('1970-01-01T00:00:00.00Z'),
        reviewer="reviewer_example",
    ) # VerdictCreationInputRequest | 

    # example passing only required values which don't have defaults set
    try:
        api_response = api_instance.create_alert_verdict(alert_id, verdict_creation_input_request)
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling AlertsApi->create_alert_verdict: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **alert_id** | **str**|  |
 **verdict_creation_input_request** | [**VerdictCreationInputRequest**](VerdictCreationInputRequest.md)|  |

### Return type

[**Verdict**](Verdict.md)

### Authorization

[ApiToken](../README.md#ApiToken)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

