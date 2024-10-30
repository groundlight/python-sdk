# API Tokens

## About API Tokens

To use the Groundlight SDK or API, you need a security token which we call an "API Token." These authenticate you to Groundlight and authorize your code to use services in your account.

API tokens look like `api_2GdXMflhJ...` and consist of a ksuid (a kind of sortable UUID) followed by a secret string.

## Handling API Tokens

**You should treat API tokens like passwords.** Never check them directly into your code or share them. Please use best security practices with your API tokens, because if anybody gets your API token, they have nearly full control over your Groundlight account.

Here are some best practices for handling API tokens:

- Store API tokens in a secure location, such as an encrypted vault.
- Use environment variables to store API tokens, rather than hardcoding them in your application.
- Limit the number of people who have access to API tokens.
- Rotate API tokens regularly and revoke old ones when they are no longer needed.

## Using API Tokens with the SDK

There are a couple of ways the SDK can find your API token:

1. Environment variable (recommended): As a best practice, we recommend storing API tokens in the environment variable `GROUNDLIGHT_API_TOKEN`. This helps avoid accidentally committing the token to your code repository.  The SDK will automatically look for the API token there, so you don't have to put it in your code at all.

```python
from groundlight import Groundlight

# looks for API token in environment variable GROUNDLIGHT_API_TOKEN
gl = Groundlight()
```

2.  Constructor argument: Alternatively, you can pass the API token directly to the Groundlight constructor. However, be cautious not to commit this code to your repository.

```
from groundlight import Groundlight

token = get_token_from_secure_location()
gl = Groundlight(api_token=token)
```

## Creating and Revoking API Tokens
You can manage your API tokens from the Groundlight website at [https://dashboard.groundlight.ai/reef/my-account/api-tokens](https://dashboard.groundlight.ai/reef/my-account/api-tokens).


### Creating API Tokens

1. Log in to your Groundlight account and navigate to the API tokens page.
1. Click the "Create New API Token" button.
1. Give the new token a descriptive name, so you can easily identify it later.
1. Click "Create Token."
1. Copy the generated token and store it securely, as you won't be able to see it again. Groundlight does not store a copy of your API tokens.

### Viewing and Revoking API Tokens

On the API tokens page, you can see a list of your current tokens, along with the following information:

- Token Name: The descriptive name you assigned when creating the token
- Snippet (prefix): A short, unique identifier for each token
- Last used: The date and time the token was last used

### To revoke an API token

1. Locate the token you want to revoke in the list.
1. Click the "Delete" button next to the token.
1. Confirm that you want to revoke the token.

Note: Revoking an API token will immediately invalidate it and prevent any applications using it from accessing your Groundlight account. Be sure to update your applications with a new token before revoking an old one.
