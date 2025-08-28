# groundlight_openapi_client.MonthToDateAccountInfoApi

All URIs are relative to *https://api.groundlight.ai/device-api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**month_to_date_account_info**](MonthToDateAccountInfoApi.md#month_to_date_account_info) | **GET** /v1/month-to-date-account-info | 


# **month_to_date_account_info**
> AccountMonthToDateInfo month_to_date_account_info()



Fetches and returns the account-specific metrics based on the current user's group.

### Example

* Api Key Authentication (ApiToken):

```python
import time
import groundlight_openapi_client
from groundlight_openapi_client.api import month_to_date_account_info_api
from groundlight_openapi_client.model.account_month_to_date_info import AccountMonthToDateInfo
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
    api_instance = month_to_date_account_info_api.MonthToDateAccountInfoApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        api_response = api_instance.month_to_date_account_info()
        pprint(api_response)
    except groundlight_openapi_client.ApiException as e:
        print("Exception when calling MonthToDateAccountInfoApi->month_to_date_account_info: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**AccountMonthToDateInfo**](AccountMonthToDateInfo.md)

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

