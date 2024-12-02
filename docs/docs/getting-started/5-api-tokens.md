# Using API Tokens

API tokens authenticate your code to access Groundlight services. They look like `api_2GdXMflhJ...` and should be treated as sensitive credentials.

The SDK can access your token in two ways:

1. **Environment Variable (Recommended)**
```python
from groundlight import Groundlight

# Automatically uses GROUNDLIGHT_API_TOKEN environment variable
gl = Groundlight()
```

2. **Direct Configuration**
```python notest
from groundlight import Groundlight

token = get_token_from_secure_location()
gl = Groundlight(api_token=token)
```

## Security Best Practices

- Store tokens in environment variables or secure vaults
- Never commit tokens to code repositories
- Limit token access to necessary personnel
- Rotate tokens periodically
- Revoke unused tokens promptly

## Managing Tokens

Access token management at [dashboard.groundlight.ai/reef/my-account/api-tokens](https://dashboard.groundlight.ai/reef/my-account/api-tokens)

### Create a Token
1. Navigate to the [API tokens page](https://dashboard.groundlight.ai/reef/my-account/api-tokens)
2. Enter a token name and click "Create API Token"
3. Save the generated token securely - it won't be shown again!

### Revoke a Token
1. Find the token in your dashboard by name
2. Click "Delete"
3. Confirm revocation

> **Important**: Update your applications with a new token before revoking an old one to prevent service interruption.