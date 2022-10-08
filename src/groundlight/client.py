import os
from io import BufferedReader, BytesIO
from typing import Optional, Union

from model import Detector, ImageQuery, PaginatedDetectorList, PaginatedImageQueryList
from openapi_client import ApiClient, Configuration
from openapi_client.api.detectors_api import DetectorsApi
from openapi_client.api.image_queries_api import ImageQueriesApi
from openapi_client.model.detector_creation_input import DetectorCreationInput

from groundlight.images import buffer_from_jpeg_file

API_TOKEN_WEB_URL = "https://app.groundlight.ai/reef/my-account/api-tokens"
API_TOKEN_VARIABLE_NAME = "GROUNDLIGHT_API_TOKEN"

GROUNDLIGHT_ENDPOINT = os.environ.get("GROUNDLIGHT_ENDPOINT", "https://api.groundlight.ai/device-api")


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

    def __init__(self, endpoint: str = GROUNDLIGHT_ENDPOINT, api_token: str = None):
        """
        :param endpoint: optionally specify a different endpoint
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

    def get_detector_by_name(self, name: str) -> Optional[Detector]:
        #TODO: Do this on server.
        detector_list = self.list_detectors(page_size=100)
        for d in detector_list.results:
            if d.name == name:
                return d
        if detector_list.next:
            #TODO: paginate
            raise RuntimeError("You have too many detectors to use get_detector_by_name")
        return None

    def list_detectors(self, page: int = 1, page_size: int = 10) -> PaginatedDetectorList:
        obj = self.detectors_api.list_detectors(page=page, page_size=page_size)
        return PaginatedDetectorList.parse_obj(obj.to_dict())

    def create_detector(self, name: str, query: str, config_name: str = None) -> Detector:
        obj = self.detectors_api.create_detector(DetectorCreationInput(name=name, query=query, config_name=config_name))
        return Detector.parse_obj(obj.to_dict())

    def get_or_create_detector(self, name: str, query: str, config_name: str = None) -> Detector:
        """Tries to look up the detector by name.  If a detector with that name and query exists, return it.
        Otherwise, create a detector with the specified query and config.
        """
        existing_detector = self.get_detector_by_name(name)
        if existing_detector:
            if existing_detector.query == query:
                return existing_detector
            else:
                raise ValueError(f"Found existing detector with {name=} (id={existing_detector.id}) but the queries don't match")
                
        return self.create_detector(name, query, config_name)

    def get_image_query(self, id: str) -> ImageQuery:
        obj = self.image_queries_api.get_image_query(id=id)
        return ImageQuery.parse_obj(obj.to_dict())

    def list_image_queries(self, page: int = 1, page_size: int = 10) -> PaginatedImageQueryList:
        obj = self.image_queries_api.list_image_queries(page=page, page_size=page_size)
        return PaginatedImageQueryList.parse_obj(obj.to_dict())

    def submit_image_query(self, 
            image: Union[str, bytes, BytesIO, BufferedReader],
            detector: Union[Detector, str],
        ) -> ImageQuery:
        """Evaluates an image with Groundlight.
        :param image: The image, in several possible formats:
            - a filename (string) of a jpeg file
            - a byte array or BytesIO with jpeg bytes
            - a numpy array in the 0-255 range (gets converted to jpeg)
        :param detector: the Detector object, or string id of a detector like `det_12345`
        """
        if isinstance(detector, Detector):
            detector_id = detector.id
        else:
            detector_id = detector
        image_bytesio: Union[BytesIO, BufferedReader]
        if isinstance(image, str):
            # Assume it is a filename
            image_bytesio = buffer_from_jpeg_file(image)
        elif isinstance(image, bytes):
            # Create a BytesIO object
            image_bytesio = BytesIO(image)
        elif isinstance(image, BytesIO) or isinstance(image, BufferedReader):
            # Already in the right format
            image_bytesio = image
        else:
            raise TypeError(
                "Unsupported type for image. We only support JPEG images specified through a filename, bytes, BytesIO, or BufferedReader object."
            )

        obj = self.image_queries_api.submit_image_query(detector_id=detector_id, body=image_bytesio)
        return ImageQuery.parse_obj(obj.to_dict())
