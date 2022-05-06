import os

from openapi_client import ApiClient, Configuration
from openapi_client.api.detectors_api import DetectorsApi
from openapi_client.api.image_queries_api import ImageQueriesApi

API_TOKEN_WEB_URL = "https://app.positronix.ai/reef/my-account/api-tokens"
API_TOKEN_VARIABLE_NAME = "GROUNDLIGHT_API_TOKEN"


class ApiTokenError(Exception):
    pass


class Groundlight(DetectorsApi, ImageQueriesApi):
    """
    A convenience wrapper around the generated API classes.
    The API token (auth) is specified through the GROUNDLIGHT_API_TOKEN environment variable.

    Example usage:
    ```
    gl = Groundlight()
    detectors = gl.list_detectors().body
    ```
    """

    def __init__(self, host: str = "https://device.positronix.ai/device-api"):
        """
        :param host: optionally specify a different endpoint
        """
        # Specify the endpoint
        configuration = Configuration(host=host)

        # Retrieve the API token from environment variable
        try:
            configuration.api_key["ApiToken"] = os.environ[API_TOKEN_VARIABLE_NAME]
        except KeyError as e:
            raise ApiTokenError(
                f'No API token found. Please put your token in an environment variable named "{API_TOKEN_VARIABLE_NAME}". If you don\'t have a token, you can create one at {API_TOKEN_WEB_URL}'
            ) from e

        super().__init__(ApiClient(configuration))
