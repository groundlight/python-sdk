import os

API_TOKEN_VARIABLE_NAME = "GROUNDLIGHT_API_TOKEN"

DEFAULT_ENDPOINT = "https://api.groundlight.ai/"
DISABLE_TLS_VARIABLE_NAME = "DISABLE_TLS_VERIFY"
SHRINK_OVERSIZED_IMAGES_VARIABLE_NAME = "GROUNDLIGHT_SHRINK_OVERSIZED_IMAGES"


__all__ = [
    "API_TOKEN_VARIABLE_NAME",
    "DEFAULT_ENDPOINT",
    "DISABLE_TLS_VARIABLE_NAME",
    "SHRINK_OVERSIZED_IMAGES_VARIABLE_NAME",
    "read_env_flag",
]


def read_env_flag(name: str, *, default: bool) -> bool:
    """Read an environment variable that must be "1" or "0".

    An unset variable returns default. The value is stripped, then "1" is True
    and "0" is False. Any other value, including a blank string, raises ValueError.
    """
    raw = os.environ.get(name)
    if raw is None:
        return default
    value = raw.strip()
    if value == "1":
        return True
    if value == "0":
        return False
    raise ValueError(f'{name} must be "1" or "0", not {raw!r}.')


API_TOKEN_MISSING_HELP_MESSAGE = (
    "No API token found. Please put your token in an environment variable "
    f'named "{API_TOKEN_VARIABLE_NAME}". If you don\'t have a token, you can '
    "create one on the API Token page of the Groundlight Dashboard."
)
