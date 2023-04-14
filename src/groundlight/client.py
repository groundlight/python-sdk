import logging
import os
import time
from io import BufferedReader, BytesIO
from typing import Optional, Union

from model import Detector, ImageQuery, PaginatedDetectorList, PaginatedImageQueryList
from openapi_client import Configuration
from openapi_client.api.detectors_api import DetectorsApi
from openapi_client.api.image_queries_api import ImageQueriesApi
from openapi_client.model.detector_creation_input import DetectorCreationInput

from groundlight.binary_labels import convert_display_label_to_internal
from groundlight.config import API_TOKEN_VARIABLE_NAME, API_TOKEN_WEB_URL
from groundlight.images import parse_supported_image_types
from groundlight.internalapi import GroundlightApiClient, sanitize_endpoint_url
from groundlight.optional_imports import Image, np

logger = logging.getLogger("groundlight.sdk")


class ApiTokenError(Exception):
    pass


class Groundlight:
    """
    Client for accessing the Groundlight cloud service.

    The API token (auth) is specified through the GROUNDLIGHT_API_TOKEN environment variable by default.

    Example usage:
    ```
    gl = Groundlight()
    d = gl.get_or_create_detector("door", "Is the door locked?")
    iq = gl.submit_image_query(d, image)
    print(iq.result)
    ```
    """

    DEFAULT_WAIT = 30

    BEFORE_POLLING_DELAY = 3.0  # Expected minimum time for a label to post
    POLLING_INITIAL_DELAY = 0.5
    POLLING_EXPONENTIAL_BACKOFF = 1.3  # This still has the nice backoff property that the max number of requests
    # is O(log(time)), but with 1.3 the guarantee is that the call will return no more than 30% late

    def __init__(self, endpoint: Optional[str] = None, api_token: str = None):
        """
        :param endpoint: optionally specify a different endpoint
        :param api_token: use this API token for your API calls. If unset, fallback to the
            environment variable "GROUNDLIGHT_API_TOKEN".
        """
        # Specify the endpoint
        self.endpoint = sanitize_endpoint_url(endpoint)
        configuration = Configuration(host=self.endpoint)

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

        self.api_client = GroundlightApiClient(configuration)
        self.detectors_api = DetectorsApi(self.api_client)
        self.image_queries_api = ImageQueriesApi(self.api_client)

    def get_detector(self, id: Union[str, Detector]) -> Detector:
        if isinstance(id, Detector):
            # Short-circuit
            return id
        obj = self.detectors_api.get_detector(id=id)
        return Detector.parse_obj(obj.to_dict())

    def get_detector_by_name(self, name: str) -> Detector:
        return self.api_client._get_detector_by_name(name)

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
        image: Union[str, bytes, Image.Image, BytesIO, BufferedReader, np.ndarray],
        wait: Optional[float] = None,
    ) -> ImageQuery:
        """Evaluates an image with Groundlight.
        :param detector: the Detector object, or string id of a detector like `det_12345`
        :param image: The image, in several possible formats:
          - filename (string) of a jpeg file
          - byte array or BytesIO or BufferedReader with jpeg bytes
          - numpy array with values 0-255 and dimensions (H,W,3) in RGB order
            (Note OpenCV uses BGR not RGB. `img[:, :, ::-1]` will reverse the channels)
          - PIL Image
          Any binary format must be JPEG-encoded already.  Any pixel format will get
          converted to JPEG at high quality before sending to service.
        :param wait: How long to wait (in seconds) for a confident answer
        """
        if wait is None:
            wait = self.DEFAULT_WAIT
        if isinstance(detector, Detector):
            detector_id = detector.id
        else:
            detector_id = detector
        image_bytesio: Union[BytesIO, BufferedReader] = parse_supported_image_types(image)

        raw_image_query = self.image_queries_api.submit_image_query(detector_id=detector_id, body=image_bytesio)
        image_query = ImageQuery.parse_obj(raw_image_query.to_dict())
        if wait:
            threshold = self.get_detector(detector).confidence_threshold
            image_query = self.wait_for_confident_result(image_query, confidence_threshold=threshold, timeout_sec=wait)
        return image_query

    def wait_for_confident_result(
        self, image_query: ImageQuery, confidence_threshold: float, timeout_sec: float = 30.0
    ) -> ImageQuery:
        """Waits for an image query result's confidence level to reach the specified value.
        Currently this is done by polling with an exponential back-off.
        :param image_query: An ImageQuery object to poll
        :param confidence_threshold: The minimum confidence level required to return before the timeout.
        :param timeout_sec: The maximum number of seconds to wait."""
        # TODO: Add support for ImageQuery id instead of object.
        timeout_time = time.time() + timeout_sec
        time.sleep(self.BEFORE_POLLING_DELAY)
        delay = self.POLLING_INITIAL_DELAY
        while time.time() < timeout_time:
            current_confidence = image_query.result.confidence
            if current_confidence is None:
                logging.debug(f"Image query with None confidence implies human label (for now)")
                break
            if current_confidence >= confidence_threshold:
                logging.debug(f"Image query confidence {current_confidence:.3f} above {confidence_threshold:.3f}")
                break
            logger.debug(
                f"Polling for updated image_query because confidence {current_confidence:.3f} < {confidence_threshold:.3f}"
            )
            time_left = max(0, time.time() - timeout_time)
            time.sleep(min(delay, time_left))
            delay *= self.POLLING_EXPONENTIAL_BACKOFF
            image_query = self.get_image_query(image_query.id)
        return image_query

    def add_label(self, image_query: Union[ImageQuery, str], label: str):
        """a new label to an image query.  This answers the detector's question.
        :param image_query: Either an ImageQuery object (returned from `submit_image_query`) or
        an image_query id as a string.
        :param label: The string "Yes" or the string "No" in answer to the query.
        """
        if isinstance(image_query, ImageQuery):
            image_query_id = image_query.id
        else:
            image_query_id = str(image_query)
            # Some old imagequery id's started with "chk_"
            if not (image_query_id.startswith("chk_") or image_query_id.startswith("iq_")):
                raise ValueError(f"Invalid image query id {image_query_id}")
        api_label = convert_display_label_to_internal(image_query_id, label)

        return self.api_client._add_label(image_query_id, api_label)
