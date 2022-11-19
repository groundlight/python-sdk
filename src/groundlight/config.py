import os

API_TOKEN_WEB_URL = "https://app.groundlight.ai/reef/my-account/api-tokens"
API_TOKEN_VARIABLE_NAME = "GROUNDLIGHT_API_TOKEN"

GROUNDLIGHT_ENDPOINT = os.environ.get("GROUNDLIGHT_ENDPOINT", "https://api.groundlight.ai/device-api")

__all__ = [
    "API_TOKEN_WEB_URL",
    "API_TOKEN_VARIABLE_NAME",
    "GROUNDLIGHT_ENDPOINT",
]