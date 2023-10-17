API_TOKEN_WEB_URL = "https://app.groundlight.ai/reef/my-account/api-tokens"
API_TOKEN_VARIABLE_NAME = "GROUNDLIGHT_API_TOKEN"

DEFAULT_ENDPOINT = "https://api.groundlight.ai/"

__all__ = [
    "API_TOKEN_WEB_URL",
    "API_TOKEN_VARIABLE_NAME",
    "DEFAULT_ENDPOINT",
]

API_TOKEN_HELP_MESSAGE = (
    "No API token found. Please put your token in an environment variable "
    f'named "{API_TOKEN_VARIABLE_NAME}". If you don\'t have a token, you can '
    f"create one at {API_TOKEN_WEB_URL}"
)
