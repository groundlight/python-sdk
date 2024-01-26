import os
from pathlib import Path
from typing import Optional

import toml

from groundlight.client import ApiTokenError
from groundlight.config import API_TOKEN_HELP_MESSAGE, API_TOKEN_VARIABLE_NAME

DEFAULT_PROFILE_NAME = "default"
CONFIG_FILE_NAME = ".myapp.toml"
API_TOKEN_CONFIG_NAME = "api_token"


def get_api_token(profile_name: str = DEFAULT_PROFILE_NAME) -> str:
    """Get the API token, or raise an ApiTokenError if it can't be found.

    :param profile_name: choose which profile to use in the TOML file
    :raises ApiTokenError: if the API token can't be found
    :return: the API token
    """
    # First, check the environment variable
    api_token = os.environ.get(API_TOKEN_VARIABLE_NAME)
    if api_token:
        return api_token

    # Next, check the TOML file
    api_token = _load_api_token_from_profile(profile_name)
    if api_token:
        return api_token

    raise ApiTokenError(API_TOKEN_HELP_MESSAGE)


def add_api_token(api_token: str, profile_name: str = DEFAULT_PROFILE_NAME) -> None:
    """Add an API token to the TOML file.

    :param api_token: the API token to add
    :param profile_name: choose which profile to use in the TOML file
    """
    # Construct the full path to the TOML file in the user's home directory
    file_path = Path.home() / CONFIG_FILE_NAME

    # Create the TOML file if it doesn't exist
    if not file_path.is_file():
        file_path.touch()

    # Read and parse the TOML file
    config_data = toml.load(file_path)

    # Add the API token to the TOML file
    profile_data = config_data.setdefault(profile_name, {})
    profile_data[API_TOKEN_CONFIG_NAME] = api_token

    # Write the TOML file
    with open(file_path, "w", encoding="utf-8") as f:
        toml.dump(config_data, f)


def _load_api_token_from_profile(profile_name: str) -> Optional[str]:
    """Load the API token from the TOML file.

    :param profile_name: choose which profile to use in the TOML file
    :return: the API token, or None if it can't be found
    """
    # Construct the full path to the TOML file in the user's home directory
    file_path = Path.home() / CONFIG_FILE_NAME

    # Check if the file exists
    if not file_path.is_file():
        return None

    # Read and parse the TOML file
    config_data = toml.load(file_path)
    profile_data = config_data.get(profile_name, {})
    return profile_data.get(API_TOKEN_CONFIG_NAME)
