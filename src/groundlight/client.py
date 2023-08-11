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

from groundlight.binary_labels import Label, convert_display_label_to_internal, convert_internal_label_to_display
from groundlight.config import API_TOKEN_VARIABLE_NAME, API_TOKEN_WEB_URL
from groundlight.images import ByteStreamWrapper, parse_supported_image_types
from groundlight.internalapi import (
    GroundlightApiClient,
    NotFoundError,
    iq_is_confident,
    sanitize_endpoint_url,
)
from groundlight.optional_imports import Image, np

logger = logging.getLogger("groundlight.sdk")


class ApiTokenError(Exception):
    pass


class Groundlight:
    """Client for accessing the Groundlight cloud service.

    The API token (auth) is specified through the GROUNDLIGHT_API_TOKEN environment variable by default.

    Example usage:
    ```
    gl = Groundlight()
    d = gl.get_or_create_detector("door", "Is the door locked?")
    iq = gl.submit_image_query(d, image)
    print(iq.result)
    ```
    """

    DEFAULT_WAIT: float = 30.0

    POLLING_INITIAL_DELAY = 0.25
    POLLING_EXPONENTIAL_BACKOFF = 1.3  # This still has the nice backoff property that the max number of requests
    # is O(log(time)), but with 1.3 the guarantee is that the call will return no more than 30% late

    def __init__(self, endpoint: Optional[str] = None, api_token: Optional[str] = None) -> None:
        """:param endpoint: optionally specify a different endpoint
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
                    (
                        "No API token found. Please put your token in an environment variable "
                        f'named "{API_TOKEN_VARIABLE_NAME}". If you don\'t have a token, you can '
                        f"create one at {API_TOKEN_WEB_URL}"
                    ),
                ) from e

        configuration.api_key["ApiToken"] = api_token

        self.api_client = GroundlightApiClient(configuration)
        self.detectors_api = DetectorsApi(self.api_client)
        self.image_queries_api = ImageQueriesApi(self.api_client)

    def _fixup_image_query(self, iq: ImageQuery) -> ImageQuery:  # pylint: disable=no-self-use
        """Process the wire-format image query to make it more usable."""
        # Note: This might go away once we clean up the mapping logic server-side.
        iq.result.label = convert_internal_label_to_display(iq, iq.result.label)
        return iq

    def get_detector(self, id: Union[str, Detector]) -> Detector:  # pylint: disable=redefined-builtin
        if isinstance(id, Detector):
            # Short-circuit
            return id
        obj = self.detectors_api.get_detector(id=id)
        return Detector.parse_obj(obj.to_dict())

    def get_detector_by_name(self, name: str) -> Detector:
        return self.api_client._get_detector_by_name(name)  # pylint: disable=protected-access

    def list_detectors(self, page: int = 1, page_size: int = 10) -> PaginatedDetectorList:
        obj = self.detectors_api.list_detectors(page=page, page_size=page_size)
        return PaginatedDetectorList.parse_obj(obj.to_dict())

    def create_detector(
        self,
        name: str,
        query: str,
        *,
        confidence_threshold: Optional[float] = None,
        pipeline_config: Optional[str] = None,
    ) -> Detector:
        detector_creation_input = DetectorCreationInput(name=name, query=query)
        if confidence_threshold is not None:
            detector_creation_input.confidence_threshold = confidence_threshold
        if pipeline_config is not None:
            detector_creation_input.pipeline_config = pipeline_config
        obj = self.detectors_api.create_detector(detector_creation_input)
        return Detector.parse_obj(obj.to_dict())

    def get_or_create_detector(
        self,
        name: str,
        query: str,
        *,
        confidence_threshold: Optional[float] = None,
        pipeline_config: Optional[str] = None,
    ) -> Detector:
        """Tries to look up the detector by name.  If a detector with that name, query, and
        confidence exists, return it. Otherwise, create a detector with the specified query and
        config.
        """
        try:
            existing_detector = self.get_detector_by_name(name)
        except NotFoundError:
            logger.debug(f"We could not find a detector with name='{name}'. So we will create a new detector ...")
            return self.create_detector(
                name=name,
                query=query,
                confidence_threshold=confidence_threshold,
                pipeline_config=pipeline_config,
            )

        # TODO: We may soon allow users to update the retrieved detector's fields.
        if existing_detector.query != query:
            raise ValueError(
                (
                    f"Found existing detector with name={name} (id={existing_detector.id}) but the queries don't match."
                    f" The existing query is '{existing_detector.query}'."
                ),
            )
        if confidence_threshold is not None and existing_detector.confidence_threshold != confidence_threshold:
            raise ValueError(
                (
                    f"Found existing detector with name={name} (id={existing_detector.id}) but the confidence"
                    " thresholds don't match. The existing confidence threshold is"
                    f" {existing_detector.confidence_threshold}."
                ),
            )
        return existing_detector

    def get_image_query(self, id: str) -> ImageQuery:  # pylint: disable=redefined-builtin
        obj = self.image_queries_api.get_image_query(id=id)
        iq = ImageQuery.parse_obj(obj.to_dict())
        return self._fixup_image_query(iq)

    def list_image_queries(self, page: int = 1, page_size: int = 10) -> PaginatedImageQueryList:
        obj = self.image_queries_api.list_image_queries(page=page, page_size=page_size)
        image_queries = PaginatedImageQueryList.parse_obj(obj.to_dict())
        if image_queries.results is not None:
            image_queries.results = [self._fixup_image_query(iq) for iq in image_queries.results]
        return image_queries

    def submit_image_query(  # noqa: PLR0913 # pylint: disable=too-many-arguments
        self,
        detector: Union[Detector, str],
        image: Union[str, bytes, Image.Image, BytesIO, BufferedReader, np.ndarray],
        wait: Optional[float] = None,
        human_review: Optional[str] = None,
        inspection_id: Optional[str] = None,
    ) -> ImageQuery:
        """Evaluates an image with Groundlight.
        :param detector: the Detector object, or string id of a detector like `det_12345`
        :param image: The image, in several possible formats:
          - filename (string) of a jpeg file
          - byte array or BytesIO or BufferedReader with jpeg bytes
          - numpy array with values 0-255 and dimensions (H,W,3) in BGR order
            (Note OpenCV uses BGR not RGB. `img[:, :, ::-1]` will reverse the channels)
          - PIL Image
          Any binary format must be JPEG-encoded already.  Any pixel format will get
          converted to JPEG at high quality before sending to service.
        :param wait: How long to wait (in seconds) for a confident answer.
        :param human_review: If `None` or `DEFAULT`, send the image query for human review
            only if the ML prediction is not confident.
            If set to `ALWAYS`, always send the image query for human review.
            If set to `NEVER`, never send the image query for human review.
        :param inspection_id: Most users will omit this. For accounts with Inspection Reports enabled,
                              this is the ID of the inspection to associate with the image query.
        """
        if wait is None:
            wait = self.DEFAULT_WAIT

        detector_id = detector.id if isinstance(detector, Detector) else detector

        image_bytesio: ByteStreamWrapper = parse_supported_image_types(image)

        params = {"detector_id": detector_id, "body": image_bytesio}
        if wait == 0:
            params["patience_time"] = self.DEFAULT_WAIT
        else:
            params["patience_time"] = wait

        if human_review is not None:
            params["human_review"] = human_review

        # If no inspection_id is provided, we submit the image query using image_queries_api (autogenerated via OpenAPI)
        # However, our autogenerated code does not currently support inspection_id, so if an inspection_id was
        # provided, we use the private API client instead.
        if inspection_id is None:
            raw_image_query = self.image_queries_api.submit_image_query(**params)
            image_query = ImageQuery.parse_obj(raw_image_query.to_dict())
        else:
            params["inspection_id"] = inspection_id
            iq_id = self.api_client.submit_image_query_with_inspection(**params)
            image_query = self.get_image_query(iq_id)

        if wait:
            threshold = self.get_detector(detector).confidence_threshold
            image_query = self.wait_for_confident_result(image_query, confidence_threshold=threshold, timeout_sec=wait)
        return self._fixup_image_query(image_query)

    def wait_for_confident_result(
        self,
        image_query: Union[ImageQuery, str],
        confidence_threshold: float,
        timeout_sec: float = 30.0,
    ) -> ImageQuery:
        """Waits for an image query result's confidence level to reach the specified value.
        Currently this is done by polling with an exponential back-off.
        :param image_query: An ImageQuery object to poll
        :param confidence_threshold: The minimum confidence level required to return before the timeout.
        :param timeout_sec: The maximum number of seconds to wait.
        """
        # Convert from image_query_id to ImageQuery if needed.
        if isinstance(image_query, str):
            image_query = self.get_image_query(image_query)

        start_time = time.time()
        next_delay = self.POLLING_INITIAL_DELAY
        target_delay = 0.0
        image_query = self._fixup_image_query(image_query)
        while True:
            patience_so_far = time.time() - start_time
            if iq_is_confident(image_query, confidence_threshold):
                logger.debug(f"Confident answer for {image_query} after {patience_so_far:.1f}s")
                break
            if patience_so_far >= timeout_sec:
                logger.debug(f"Timeout after {timeout_sec:.0f}s waiting for {image_query}")
                break
            target_delay = min(patience_so_far + next_delay, timeout_sec)
            sleep_time = max(target_delay - patience_so_far, 0)
            logger.debug(
                f"Polling ({target_delay:.1f}/{timeout_sec:.0f}s) {image_query} until"
                f" confidence>={confidence_threshold:.3f}"
            )
            time.sleep(sleep_time)
            next_delay *= self.POLLING_EXPONENTIAL_BACKOFF
            image_query = self.get_image_query(image_query.id)
            image_query = self._fixup_image_query(image_query)
        return image_query

    def add_label(self, image_query: Union[ImageQuery, str], label: Union[Label, str]):
        """A new label to an image query.  This answers the detector's question.
        :param image_query: Either an ImageQuery object (returned from `submit_image_query`) or
        an image_query id as a string.
        :param label: The string "YES" or the string "NO" in answer to the query.
        """
        if isinstance(image_query, ImageQuery):
            image_query_id = image_query.id
        else:
            image_query_id = str(image_query)
            # Some old imagequery id's started with "chk_"
            if not image_query_id.startswith(("chk_", "iq_")):
                raise ValueError(f"Invalid image query id {image_query_id}")
        api_label = convert_display_label_to_internal(image_query_id, label)

        return self.api_client._add_label(image_query_id, api_label)  # pylint: disable=protected-access

    def start_inspection(self) -> str:
        """For users with Inspection Reports enabled only.
        Starts an inspection report and returns the id of the inspection.
        """
        return self.api_client.start_inspection()

    def update_inspection_metadata(self, inspection_id: str, user_provided_key: str, user_provided_value: str) -> None:
        """For users with Inspection Reports enabled only.
        Add/update inspection metadata with the user_provided_key and user_provided_value.
        """
        self.api_client.update_inspection_metadata(inspection_id, user_provided_key, user_provided_value)

    def stop_inspection(self, inspection_id: str) -> str:
        """For users with Inspection Reports enabled only.
        Stops an inspection and raises an exception if the response from the server
        indicates that the inspection was not successfully stopped.
        Returns a str with result of the inspection (either PASS or FAIL).
        """
        return self.api_client.stop_inspection(inspection_id)

    def update_detector_confidence_threshold(self, detector_id: str, confidence_threshold: float) -> None:
        """Updates the confidence threshold of a detector given a detector_id."""
        self.api_client.update_detector_confidence_threshold(detector_id, confidence_threshold)
