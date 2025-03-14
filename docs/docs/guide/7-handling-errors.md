# Handling Errors

When building applications with the Groundlight SDK, you may encounter errors during API calls. This page covers how to handle such errors and build robust code that can gracefully handle exceptions.

## Handling `ApiException`

In the event of an HTTP error during an API call, the Groundlight SDK raises an `ApiException`. This exception provides access to various metadata:

```python notest
import traceback
from groundlight import ApiException, Groundlight

gl = Groundlight()
try:
    d = gl.get_or_create_detector(
        name="Road Checker",
        query="Is the site access road blocked?",
    )
    iq = gl.submit_image_query(d, get_image(), wait=60)
except ApiException as e:
    # Print a traceback for debugging
    traceback.print_exc()

    # e.reason contains a textual description of the error
    print(f"Error reason: {e.reason}")

    # e.status contains the HTTP status code
    print(f"HTTP status code: {e.status}")

    # Common HTTP status codes:
    # 400 Bad Request: The request was invalid or malformed
    # 401 Unauthorized: Your GROUNDLIGHT_API_TOKEN is missing or invalid
    # 403 Forbidden: The request is not allowed due to insufficient permissions
    # 404 Not Found: The requested resource was not found
    # 429 Too Many Requests: The rate limit for the API has been exceeded
    # 500 Internal Server Error: An error occurred on the server side
```

## Best Practices for Handling Exceptions

When working with the Groundlight SDK, follow these best practices to handle exceptions and build robust code:

### Catch Specific Exceptions

Catch only the specific exceptions that you expect to be raised, such as `ApiException`. Avoid catching broad exceptions like `Exception`, as it may make debugging difficult and obscure other unrelated issues.

### Use Custom Exception Classes

Consider creating custom exception classes for your application-specific errors. This can help you differentiate between errors originating from the Groundlight SDK and those from your application.

### Log Exceptions

Log exceptions using appropriate log levels (e.g., error, warning) and include relevant context. This practice aids in effective debugging and monitoring application health.

### Implement Retry Logic

Incorporate retry logic with exponential backoff for transient errors, such as network issues or rate limits. This strategy allows your application to recover from temporary problems automatically.

### Handle Exceptions Gracefully

Ensure your application remains functional despite errors by handling exceptions gracefully. This might involve displaying user-friendly error messages or reverting to default behaviors.

### Test Your Error Handling

Write tests to ensure that your error handling works as expected. This can help you catch issues early and ensure that your application can handle errors gracefully in production.

By following these best practices, you can create robust and resilient applications that can handle server errors and other exceptions when using the Groundlight SDK.
