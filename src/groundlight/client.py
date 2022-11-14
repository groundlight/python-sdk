from io import BufferedReader, BytesIO
import logging
import os
import time
from typing import Optional, Union

from model import Detector, ImageQuery, PaginatedDetectorList, PaginatedImageQueryList
from openapi_client import ApiClient, Configuration
from openapi_client.api.detectors_api import DetectorsApi
from openapi_client.api.image_queries_api import ImageQueriesApi
from openapi_client.model.detector_creation_input import DetectorCreationInput

from groundlight.images import buffer_from_jpeg_file, jpeg_from_numpy
from groundlight.optional_imports import np

API_TOKEN_WEB_URL = "https://app.groundlight.ai/reef/my-account/api-tokens"
API_TOKEN_VARIABLE_NAME = "GROUNDLIGHT_API_TOKEN"

GROUNDLIGHT_ENDPOINT = os.environ.get("GROUNDLIGHT_ENDPOINT", "https://api.groundlight.ai/device-api")

logger = logging.getLogger("groundlight")


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

    def get_detector(self, id: Union[str, Detector]) -> Detector:
        if isinstance(id, Detector):
            # Short-circuit
            return id
        obj = self.detectors_api.get_detector(id=id)
        return Detector.parse_obj(obj.to_dict())

    def get_detector_by_name(self, name: str) -> Optional[Detector]:
        # TODO: Do this on server.
        detector_list = self.list_detectors(page_size=100)
        for d in detector_list.results:
            if d.name == name:
                return d
        if detector_list.next:
            # TODO: paginate
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
                raise ValueError(
                    f"Found existing detector with name={name} (id={existing_detector.id}) but the queries don't match"
                )

        return self.create_detector(name, query, config_name)

    def get_image_query(self, id: str) -> ImageQuery:
        obj = self.image_queries_api.get_image_query(id=id)
        return ImageQuery.parse_obj(obj.to_dict())

    def list_image_queries(self, page: int = 1, page_size: int = 10) -> PaginatedImageQueryList:
        obj = self.image_queries_api.list_image_queries(page=page, page_size=page_size)
        return PaginatedImageQueryList.parse_obj(obj.to_dict())

    def submit_image_query(
        self,
        detector: Union[Detector, str],
        image: Union[str, bytes, BytesIO, BufferedReader, np.ndarray],
        wait: float = 0,
    ) -> ImageQuery:
        """Evaluates an image with Groundlight.
        :param detector: the Detector object, or string id of a detector like `det_12345`
        :param image: The image, in several possible formats:
            - a filename (string) of a jpeg file
            - a byte array or BytesIO with jpeg bytes
            - a numpy array in the 0-255 range (gets converted to jpeg)
        :param wait: How long to wait (in seconds) for a confident answer
        """
        if isinstance(detector, Detector):
            detector_id = detector.id
        else:
            detector_id = detector
        image_bytesio: Union[BytesIO, BufferedReader]
        # TODO: support PIL Images
        if isinstance(image, str):
            # Assume it is a filename
            image_bytesio = buffer_from_jpeg_file(image)
        elif isinstance(image, bytes):
            # Create a BytesIO object
            image_bytesio = BytesIO(image)
        elif isinstance(image, BytesIO) or isinstance(image, BufferedReader):
            # Already in the right format
            image_bytesio = image
        elif isinstance(image, np.ndarray):
            image_bytesio = BytesIO(jpeg_from_numpy(image))
        else:
            raise TypeError(
                "Unsupported type for image. We only support numpy arrays (3,W,H) or JPEG images specified through a filename, bytes, BytesIO, or BufferedReader object."
            )

        raw_img_query = self.image_queries_api.submit_image_query(detector_id=detector_id, body=image_bytesio)
        img_query = ImageQuery.parse_obj(raw_img_query.to_dict())
        if wait:
            threshold = self.get_detector(detector).confidence_threshold
            img_query = self._poll_for_confident_result(img_query, wait, threshold)
        return img_query

    def _poll_for_confident_result(self, img_query: ImageQuery, wait: float, threshold: float) -> ImageQuery:
        """Polls on an image query waiting for the result to reach the specified confidence."""
        start_time = time.time()
        delay = 0.1
        while time.time() - start_time < wait:
            current_confidence = img_query.result.confidence
            if current_confidence is None:
                logging.debug(f"Image query with None confidence implies human label (for now)")
                break
            if current_confidence >= threshold:
                logging.debug(f"Image query confidence {current_confidence:.3f} above {threshold:.3f}")
                break
            logger.debug(
                f"Polling for updated image_query because confidence {current_confidence:.3f} < {threshold:.3f}"
            )
            time.sleep(delay)
            delay *= 1.4  # slow exponential backoff
            img_query = self.get_image_query(img_query.id)
        return img_query
