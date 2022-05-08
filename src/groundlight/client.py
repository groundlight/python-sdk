import os
from io import BytesIO

from model import Detector, ImageQuery, PaginatedDetectorList, PaginatedImageQueryList
from openapi_client import ApiClient, Configuration
from openapi_client.api.detectors_api import DetectorsApi
from openapi_client.api.image_queries_api import ImageQueriesApi
from openapi_client.model.detector_creation_input import DetectorCreationInput

API_TOKEN_WEB_URL = "https://app.positronix.ai/reef/my-account/api-tokens"
API_TOKEN_VARIABLE_NAME = "GROUNDLIGHT_API_TOKEN"


class ApiTokenError(Exception):
    pass


class Groundlight:
    """
    A convenience wrapper around the generated API classes.
    The API token (auth) is specified through the GROUNDLIGHT_API_TOKEN environment variable by default.

    Example usage:
    ```
    gl = Groundlight()
    detectors = gl.list_detectors()
    ```
    """

    def __init__(self, endpoint: str = "https://device.positronix.ai/device-api", api_token: str = None):
        """
        :param endpoint: optionally specify a different endpoint. E.g.
            - Prod (default): https://device.positronix.ai/device-api
            - Integ: https://device.integ.positronix.ai/device-api
            - Localhost tunnel to a GPU instance: http://localhost:8000/device-api
        :param api_token: use this API token for your API calls. If unset, fallback to the
            environment variable "GROUNDLIGHT_API_TOKEN".
        """
        # Specify the endpoint
        configuration = Configuration(host=endpoint)

        if api_token is None:
            try:
                # Retrieve the API token from environment variable
                api_token = os.environ[API_TOKEN_VARIABLE_NAME]
            except KeyError as e:
                raise ApiTokenError(
                    "No API token found. Please put your token in an environment variable "
                    f'named "{API_TOKEN_VARIABLE_NAME}". If you don\'t have a token, you can '
                    f"create one at {API_TOKEN_WEB_URL}"
                ) from e

        configuration.api_key["ApiToken"] = api_token

        self.detectors_api = DetectorsApi(ApiClient(configuration))
        self.image_queries_api = ImageQueriesApi(ApiClient(configuration))

    def get_detector(self, id: str) -> Detector:
        obj = self.detectors_api.get_detector(id=id)
        return Detector.parse_obj(obj.to_dict())

    def list_detectors(self, page: int = 1, page_size: int = 10) -> PaginatedDetectorList:
        obj = self.detectors_api.list_detectors(page=page, page_size=page_size)
        return PaginatedDetectorList.parse_obj(obj.to_dict())

    def create_detector(self, name: str, query: str) -> Detector:
        obj = self.detectors_api.create_detector(DetectorCreationInput(name=name, query=query))
        return Detector.parse_obj(obj.to_dict())

    def get_image_query(self, id: str) -> ImageQuery:
        obj = self.image_queries_api.get_image_query(id=id)
        return ImageQuery.parse_obj(obj.to_dict())

    def list_image_queries(self, page: int = 1, page_size: int = 10) -> PaginatedImageQueryList:
        obj = self.image_queries_api.list_image_queries(page=page, page_size=page_size)
        return PaginatedImageQueryList.parse_obj(obj.to_dict())

    def submit_image_query(self, detector_id: str, image_bytesio: BytesIO) -> ImageQuery:
        obj = self.image_queries_api.submit_image_query(detector_id=detector_id, body=image_bytesio)
        return ImageQuery.parse_obj(obj.to_dict())
