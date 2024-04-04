import logging
import os
import time
import warnings
from functools import partial
from io import BufferedReader, BytesIO
from typing import Callable, Optional, Union

from groundlight_openapi_client import Configuration
from groundlight_openapi_client.api.detectors_api import DetectorsApi
from groundlight_openapi_client.api.image_queries_api import ImageQueriesApi
from groundlight_openapi_client.api.user_api import UserApi
from groundlight_openapi_client.exceptions import NotFoundException, UnauthorizedException
from groundlight_openapi_client.model.detector_creation_input import DetectorCreationInput
from model import (
    Detector,
    ImageQuery,
    PaginatedDetectorList,
    PaginatedImageQueryList,
)
from urllib3.exceptions import InsecureRequestWarning

from groundlight.binary_labels import Label, convert_display_label_to_internal, convert_internal_label_to_display
from groundlight.config import API_TOKEN_MISSING_HELP_MESSAGE, API_TOKEN_VARIABLE_NAME, DISABLE_TLS_VARIABLE_NAME
from groundlight.encodings import url_encode_dict
from groundlight.images import ByteStreamWrapper, parse_supported_image_types
from groundlight.internalapi import (
    GroundlightApiClient,
    NotFoundError,
    iq_is_answered,
    iq_is_confident,
    sanitize_endpoint_url,
)
from groundlight.optional_imports import Image, np

logger = logging.getLogger("groundlight.sdk")

# Set urllib3 request timeout to something modern and fast.
# The system defaults can be stupidly long
# It used to take >8 min to timeout to a bad IP address
DEFAULT_REQUEST_TIMEOUT = 10  # seconds


class GroundlightClientError(Exception):
    pass


class ApiTokenError(GroundlightClientError):
    pass


class Groundlight:
    """
    Client for accessing the Groundlight cloud service.

    The API token (auth) is specified through the **GROUNDLIGHT_API_TOKEN** environment variable by default.

    **Example usage**::

        gl = Groundlight()
        detector = gl.get_or_create_detector(
                        name="door",
                        query="Is the door locked?",
                        confidence_threshold=0.9
                    )
        image_query = gl.submit_image_query(
                        detector=detector,
                        image="path/to/image.jpeg",
                        wait=0.0,
                        human_review="ALWAYS"
                    )
        print(f"Image query confidence = {image_query.result.confidence}")

        # Poll the backend service for a confident answer
        image_query = gl.wait_for_confident_result(
                        image_query=image_query,
                        confidence_threshold=0.9,
                        timeout_sec=60.0
                    )

        # Examine new confidence after a continuously trained ML model has re-evaluated the image query
        print(f"Image query confidence = {image_query.result.confidence}")
    """

    DEFAULT_WAIT: float = 30.0

    POLLING_INITIAL_DELAY = 0.25
    POLLING_EXPONENTIAL_BACKOFF = 1.3  # This still has the nice backoff property that the max number of requests
    # is O(log(time)), but with 1.3 the guarantee is that the call will return no more than 30% late

    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_token: Optional[str] = None,
        disable_tls_verification: Optional[bool] = None,
    ) -> None:
        """
        Constructs a Groundlight client.

        :param endpoint: optionally specify a different endpoint

        :param api_token: use this API token for your API calls.
                        If unset, fallback to the environment variable "GROUNDLIGHT_API_TOKEN".

        :param disable_tls_verification: Set this to `True` to skip verifying SSL/TLS certificates
                                        when calling API from https server. If unset, the fallback will check
                                        the environment variable "DISABLE_TLS_VERIFY" for `1` or `0`. By default,
                                        certificates are verified.

                                        Disable verification if using a self-signed TLS certificate with a Groundlight
                                        Edge Endpoint.  It is unadvised to disable verification  if connecting directly
                                        to the Groundlight cloud service.
        :type disable_tls_verification: Optional[bool]

        :return: Groundlight client
        """
        # Specify the endpoint
        self.endpoint = sanitize_endpoint_url(endpoint)
        self.configuration = Configuration(host=self.endpoint)

        if not api_token:
            try:
                # Retrieve the API token from environment variable
                api_token = os.environ[API_TOKEN_VARIABLE_NAME]
            except KeyError as e:
                raise ApiTokenError(API_TOKEN_MISSING_HELP_MESSAGE) from e
            if not api_token:
                raise ApiTokenError("No API token found.  GROUNDLIGHT_API_TOKEN environment variable is set but blank")
        self.api_token_prefix = api_token[:12]

        should_disable_tls_verification = disable_tls_verification

        if should_disable_tls_verification is None:
            should_disable_tls_verification = bool(int(os.environ.get(DISABLE_TLS_VARIABLE_NAME, 0)))

        if should_disable_tls_verification:
            logger.warning(
                "Disabling SSL/TLS certificate verification.  This should only be used when connecting to an endpoint"
                " with a self-signed certificate."
            )
            warnings.simplefilter("ignore", InsecureRequestWarning)

            self.configuration.verify_ssl = False
            self.configuration.assert_hostname = False

        self.configuration.api_key["ApiToken"] = api_token

        self.api_client = GroundlightApiClient(self.configuration)
        self.detectors_api = DetectorsApi(self.api_client)
        self.image_queries_api = ImageQueriesApi(self.api_client)
        self.user_api = UserApi(self.api_client)
        self._verify_connectivity()

    def __repr__(self) -> str:
        return f"Logged in as {self.whoami()} to Groundlight at {self.endpoint}"

    def _verify_connectivity(self) -> None:
        """
        Verify that the client can connect to the Groundlight service, and raise a helpful
        exception if it cannot.
        """
        try:
            # a simple query to confirm that the endpoint & API token are working
            self.whoami()
        except UnauthorizedException as e:
            msg = (
                f"Invalid API token '{self.api_token_prefix}...' connecting to endpoint "
                f"'{self.endpoint}'.  Endpoint is responding, but API token is probably invalid."
            )
            raise ApiTokenError(msg) from e
        except Exception as e:
            msg = (
                f"Error connecting to Groundlight using API token '{self.api_token_prefix}...'"
                f" at endpoint '{self.endpoint}'.  Endpoint might be invalid or unreachable? "
                "Check https://status.groundlight.ai/ for service status."
            )
            raise GroundlightClientError(msg) from e

    @staticmethod
    def _fixup_image_query(iq: ImageQuery) -> ImageQuery:
        """
        Process the wire-format image query to make it more usable.
        """
        # Note: This might go away once we clean up the mapping logic server-side.

        # we have to check that result is not None because the server will return a result of None if want_async=True
        if iq.result is not None:
            iq.result.label = convert_internal_label_to_display(iq, iq.result.label)
        return iq

    def whoami(self) -> str:
        """
        Return the username associated with the API token.

        :return: str
        """
        obj = self.user_api.who_am_i()
        return obj["username"]

    def get_detector(self, id: Union[str, Detector]) -> Detector:  # pylint: disable=redefined-builtin
        """
        Get a detector by id

        :param id: the detector id

        :return: Detector
        """

        if isinstance(id, Detector):
            # Short-circuit
            return id
        try:
            obj = self.detectors_api.get_detector(id=id, _request_timeout=DEFAULT_REQUEST_TIMEOUT)
        except NotFoundException as e:
            raise NotFoundError(f"Detector with id '{id}' not found") from e
        return Detector.parse_obj(obj.to_dict())

    def get_detector_by_name(self, name: str) -> Detector:
        """
        Get a detector by name

        :param name: the detector name

        :return: Detector
        """
        return self.api_client._get_detector_by_name(name)  # pylint: disable=protected-access

    def list_detectors(self, page: int = 1, page_size: int = 10) -> PaginatedDetectorList:
        """
        List out detectors you own

        :param page: the page number

        :param page_size: the page size

        :return: PaginatedDetectorList
        """
        obj = self.detectors_api.list_detectors(
            page=page, page_size=page_size, _request_timeout=DEFAULT_REQUEST_TIMEOUT
        )
        return PaginatedDetectorList.parse_obj(obj.to_dict())

    def create_detector(
        self,
        name: str,
        query: str,
        *,
        confidence_threshold: Optional[float] = None,
        pipeline_config: Optional[str] = None,
        metadata: Union[dict, str, None] = None,
    ) -> Detector:
        """
        Create a new detector with a given name and query

        :param name: the detector name

        :param query: the detector query

        :param confidence_threshold: the confidence threshold

        :param pipeline_config: the pipeline config

        :param metadata: A dictionary or JSON string of custom key/value metadata to associate with
            the detector (limited to 1KB). You can retrieve this metadata later by calling
            `get_detector()`.

        :return: Detector
        """
        detector_creation_input = DetectorCreationInput(name=name, query=query)
        if confidence_threshold is not None:
            detector_creation_input.confidence_threshold = confidence_threshold
        if pipeline_config is not None:
            detector_creation_input.pipeline_config = pipeline_config
        if metadata is not None:
            detector_creation_input.metadata = str(url_encode_dict(metadata, name="metadata", size_limit_bytes=1024))
        obj = self.detectors_api.create_detector(detector_creation_input, _request_timeout=DEFAULT_REQUEST_TIMEOUT)
        return Detector.parse_obj(obj.to_dict())

    def get_or_create_detector(
        self,
        name: str,
        query: str,
        *,
        confidence_threshold: Optional[float] = None,
        pipeline_config: Optional[str] = None,
        metadata: Union[dict, str, None] = None,
    ) -> Detector:
        """
        Tries to look up the detector by name.  If a detector with that name, query, and
        confidence exists, return it. Otherwise, create a detector with the specified query and
        config.

        :param name: the detector name

        :param query: the detector query

        :param confidence_threshold: the confidence threshold

        :param pipeline_config: the pipeline config

        :param metadata: A dictionary or JSON string of custom key/value metadata to associate with
            the detector (limited to 1KB). You can retrieve this metadata later by calling
            `get_detector()`.

        :return: Detector
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
                metadata=metadata,
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
        """
        Get an image query by id

        :param id: the image query id

        :return: ImageQuery
        """
        obj = self.image_queries_api.get_image_query(id=id, _request_timeout=DEFAULT_REQUEST_TIMEOUT)
        iq = ImageQuery.parse_obj(obj.to_dict())
        return self._fixup_image_query(iq)

    def list_image_queries(self, page: int = 1, page_size: int = 10) -> PaginatedImageQueryList:
        """
        List out image queries you own

        :param page: the page number

        :param page_size: the page size

        :return: PaginatedImageQueryList
        """
        obj = self.image_queries_api.list_image_queries(
            page=page, page_size=page_size, _request_timeout=DEFAULT_REQUEST_TIMEOUT
        )
        image_queries = PaginatedImageQueryList.parse_obj(obj.to_dict())
        if image_queries.results is not None:
            image_queries.results = [self._fixup_image_query(iq) for iq in image_queries.results]
        return image_queries

    def submit_image_query(  # noqa: PLR0913 # pylint: disable=too-many-arguments, too-many-locals
        self,
        detector: Union[Detector, str],
        image: Union[str, bytes, Image.Image, BytesIO, BufferedReader, np.ndarray],
        wait: Optional[float] = None,
        patience_time: Optional[float] = None,
        confidence_threshold: Optional[float] = None,
        human_review: Optional[str] = None,
        want_async: bool = False,
        inspection_id: Optional[str] = None,
        metadata: Union[dict, str, None] = None,
    ) -> ImageQuery:
        """
        Evaluates an image with Groundlight.

        :param detector: the Detector object, or string id of a detector like `det_12345`

        :param image: The image, in several possible formats:
          - filename (string) of a jpeg file
          - byte array or BytesIO or BufferedReader with jpeg bytes
          - numpy array with values 0-255 and dimensions (H,W,3) in BGR order
            (Note OpenCV uses BGR not RGB. `img[:, :, ::-1]` will reverse the channels)
          - PIL Image: Any binary format must be JPEG-encoded already.
            Any pixel format will get converted to JPEG at high quality before sending to service.

        :param wait: How long to poll (in seconds) for a confident answer. This is a client-side timeout.

        :param patience_time: How long to wait (in seconds) for a confident answer for this image query.
            The longer the patience_time, the more likely Groundlight will arrive at a confident answer.
            Within patience_time, Groundlight will update ML predictions based on stronger findings,
            and, additionally, Groundlight will prioritize human review of the image query if necessary.
            This is a soft server-side timeout. If not set, use the detector's patience_time.

        :param confidence_threshold: The confidence threshold to wait for.
            If not set, use the detector's confidence threshold.

        :param human_review: If `None` or `DEFAULT`, send the image query for human review
            only if the ML prediction is not confident.
            If set to `ALWAYS`, always send the image query for human review.
            If set to `NEVER`, never send the image query for human review.

        :param want_async: If True, the client will return as soon as the image query is submitted and will not wait for
            an ML/human prediction. The returned `ImageQuery` will have a `result` of None. Must set `wait` to 0 to use
            want_async.

        :param inspection_id: Most users will omit this. For accounts with Inspection Reports enabled,
                            this is the ID of the inspection to associate with the image query.

        :param metadata: A dictionary or JSON string of custom key/value metadata to associate with
            the image query (limited to 1KB). You can retrieve this metadata later by calling
            `get_image_query()`.

        :return: ImageQuery
        """
        if wait is None:
            wait = self.DEFAULT_WAIT

        detector_id = detector.id if isinstance(detector, Detector) else detector

        image_bytesio: ByteStreamWrapper = parse_supported_image_types(image)

        params = {"detector_id": detector_id, "body": image_bytesio, "_request_timeout": DEFAULT_REQUEST_TIMEOUT}

        if patience_time is not None:
            params["patience_time"] = patience_time

        if human_review is not None:
            params["human_review"] = human_review

        if inspection_id:  # consider an empty string to mean there is no inspection
            params["inspection_id"] = inspection_id

        if want_async is True:
            # If want_async is True, we don't want to wait for a result. As a result wait must be set to 0 to use
            # want_async.
            if wait != 0:
                raise ValueError(
                    "wait must be set to 0 to use want_async. Using wait and want_async at the same time is incompatible."  # noqa: E501
                )
            params["want_async"] = str(bool(want_async))

        if metadata is not None:
            # Currently, our backend server puts the image in the body data of the API request,
            # which means we need to put the metadata in the query string. To do that safely, we
            # url- and base64-encode the metadata.
            params["metadata"] = url_encode_dict(metadata, name="metadata", size_limit_bytes=1024)

        raw_image_query = self.image_queries_api.submit_image_query(**params)
        image_query = ImageQuery.parse_obj(raw_image_query.to_dict())

        if wait > 0:
            if confidence_threshold is None:
                threshold = self.get_detector(detector).confidence_threshold
            else:
                threshold = confidence_threshold
            image_query = self.wait_for_confident_result(image_query, confidence_threshold=threshold, timeout_sec=wait)

        return self._fixup_image_query(image_query)

    def ask_confident(  # noqa: PLR0913 # pylint: disable=too-many-arguments
        self,
        detector: Union[Detector, str],
        image: Union[str, bytes, Image.Image, BytesIO, BufferedReader, np.ndarray],
        confidence_threshold: Optional[float] = None,
        wait: Optional[float] = None,
        metadata: Union[dict, str, None] = None,
        inspection_id: Optional[str] = None,
    ) -> ImageQuery:
        """
        Evaluates an image with Groundlight waiting until an answer above the confidence threshold
        of the detector is reached or the wait period has passed.

        :param detector: the Detector object, or string id of a detector like `det_12345`

        :param image: The image, in several possible formats:
          - filename (string) of a jpeg file
          - byte array or BytesIO or BufferedReader with jpeg bytes
          - numpy array with values 0-255 and dimensions (H,W,3) in BGR order
            (Note OpenCV uses BGR not RGB. `img[:, :, ::-1]` will reverse the channels)
          - PIL Image
          Any binary format must be JPEG-encoded already.  Any pixel format will get
          converted to JPEG at high quality before sending to service.

        :param confidence_threshold: The confidence threshold to wait for.
            If not set, use the detector's confidence threshold.

        :param wait: How long to wait (in seconds) for a confident answer.

        :param metadata: A dictionary or JSON string of custom key/value metadata to associate with
            the image query (limited to 1KB). You can retrieve this metadata later by calling
            `get_image_query()`.

        :return: ImageQuery
        """
        return self.submit_image_query(
            detector,
            image,
            confidence_threshold=confidence_threshold,
            wait=wait,
            patience_time=wait,
            human_review=None,
            metadata=metadata,
            inspection_id=inspection_id,
        )

    def ask_ml(  # noqa: PLR0913 # pylint: disable=too-many-arguments, too-many-locals
        self,
        detector: Union[Detector, str],
        image: Union[str, bytes, Image.Image, BytesIO, BufferedReader, np.ndarray],
        wait: Optional[float] = None,
        metadata: Union[dict, str, None] = None,
        inspection_id: Optional[str] = None,
    ) -> ImageQuery:
        """
        Evaluates an image with Groundlight, getting the first answer Groundlight can provide.

        :param detector: the Detector object, or string id of a detector like `det_12345`

        :param image: The image, in several possible formats:
          - filename (string) of a jpeg file
          - byte array or BytesIO or BufferedReader with jpeg bytes
          - numpy array with values 0-255 and dimensions (H,W,3) in BGR order
            (Note OpenCV uses BGR not RGB. `img[:, :, ::-1]` will reverse the channels)
          - PIL Image
          Any binary format must be JPEG-encoded already.  Any pixel format will get
          converted to JPEG at high quality before sending to service.

        :param wait: How long to wait (in seconds) for any answer.

        :param metadata: A dictionary or JSON string of custom key/value metadata to associate with
            the image query (limited to 1KB). You can retrieve this metadata later by calling
            `get_image_query()`.

        :return: ImageQuery
        """
        iq = self.submit_image_query(
            detector,
            image,
            wait=0,
            metadata=metadata,
            inspection_id=inspection_id,
        )
        if iq_is_answered(iq):
            return iq
        wait = self.DEFAULT_WAIT if wait is None else wait
        return self.wait_for_ml_result(iq, timeout_sec=wait)

    def ask_async(  # noqa: PLR0913 # pylint: disable=too-many-arguments
        self,
        detector: Union[Detector, str],
        image: Union[str, bytes, Image.Image, BytesIO, BufferedReader, np.ndarray],
        patience_time: Optional[float] = None,
        confidence_threshold: Optional[float] = None,
        human_review: Optional[str] = None,
        metadata: Union[dict, str, None] = None,
        inspection_id: Optional[str] = None,
    ) -> ImageQuery:
        """
        Convenience method for submitting an `ImageQuery` asynchronously. This is equivalent to calling
        `submit_image_query` with `want_async=True` and `wait=0`. Use `get_image_query` to retrieve the `result` of the
        ImageQuery.

        :param detector: the Detector object, or string id of a detector like `det_12345`

        :param image: The image, in several possible formats:

          - filename (string) of a jpeg file
          - byte array or BytesIO or BufferedReader with jpeg bytes
          - numpy array with values 0-255 and dimensions (H,W,3) in BGR order
            (Note OpenCV uses BGR not RGB. `img[:, :, ::-1]` will reverse the channels)
          - PIL Image: Any binary format must be JPEG-encoded already.
            Any pixel format will get converted to JPEG at high quality before sending to service.


        :param patience_time: How long to wait (in seconds) for a confident answer for this image query.
            The longer the patience_time, the more likely Groundlight will arrive at a confident answer.
            Within patience_time, Groundlight will update ML predictions based on stronger findings,
            and, additionally, Groundlight will prioritize human review of the image query if necessary.
            This is a soft server-side timeout. If not set, use the detector's patience_time.

        :param confidence_threshold: The confidence threshold to wait for.
            If not set, use the detector's confidence threshold.

        :param human_review: If `None` or `DEFAULT`, send the image query for human review
            only if the ML prediction is not confident.
            If set to `ALWAYS`, always send the image query for human review.
            If set to `NEVER`, never send the image query for human review.

        :param inspection_id: Most users will omit this. For accounts with Inspection Reports enabled,
                            this is the ID of the inspection to associate with the image query.

        :param metadata: A dictionary or JSON string of custom key/value metadata to associate with
            the image query (limited to 1KB). You can retrieve this metadata later by calling
            `get_image_query()`.

        :return: ImageQuery


        **Example usage**::

            gl = Groundlight()
            detector = gl.get_or_create_detector(
                            name="door",
                            query="Is the door locked?",
                            confidence_threshold=0.9
                        )

            image_query = gl.ask_async(
                            detector=detector,
                            image="path/to/image.jpeg")

            # the image_query will have an id for later retrieval
            assert image_query.id is not None

            # Do not attempt to access the result of this query as the result for all async queries
            # will be None. Your result is being computed asynchronously and will be available later
            assert image_query.result is None

            # retrieve the result later or on another machine by calling gl.wait_for_confident_result()
            # with the id of the image_query above. This will block until the result is available.
            image_query = gl.wait_for_confident_result(image_query.id)

            # now the result will be available for your use
            assert image_query.result is not None

            # alternatively, you can check if the result is available (without blocking) by calling
            # gl.get_image_query() with the id of the image_query above.
            image_query = gl.get_image_query(image_query.id)
        """
        return self.submit_image_query(
            detector,
            image,
            wait=0,
            patience_time=patience_time,
            confidence_threshold=confidence_threshold,
            human_review=human_review,
            want_async=True,
            metadata=metadata,
            inspection_id=inspection_id,
        )

    def wait_for_confident_result(
        self,
        image_query: Union[ImageQuery, str],
        confidence_threshold: Optional[float] = None,
        timeout_sec: float = 30.0,
    ) -> ImageQuery:
        """
        Waits for an image query result's confidence level to reach the specified value.
        Currently this is done by polling with an exponential back-off.

        :param image_query: An ImageQuery object to poll

        :param confidence_threshold: The confidence threshold to wait for.
            If not set, use the detector's confidence threshold.

        :param timeout_sec: The maximum number of seconds to wait.

        :return: ImageQuery
        """
        if confidence_threshold is None:
            if isinstance(image_query, str):
                image_query = self.get_image_query(image_query)
            confidence_threshold = self.get_detector(image_query.detector_id).confidence_threshold

        confidence_above_thresh = partial(iq_is_confident, confidence_threshold=confidence_threshold)
        return self._wait_for_result(image_query, condition=confidence_above_thresh, timeout_sec=timeout_sec)

    def wait_for_ml_result(self, image_query: Union[ImageQuery, str], timeout_sec: float = 30.0) -> ImageQuery:
        """Waits for the first ml result to be returned.
        Currently this is done by polling with an exponential back-off.

        :param image_query: An ImageQuery object to poll

        :param timeout_sec: The maximum number of seconds to wait.

        :return: ImageQuery
        """
        return self._wait_for_result(image_query, condition=iq_is_answered, timeout_sec=timeout_sec)

    def _wait_for_result(
        self, image_query: Union[ImageQuery, str], condition: Callable, timeout_sec: float = 30.0
    ) -> ImageQuery:
        """Performs polling with exponential back-off until the condition is met for the image query.

        :param image_query: An ImageQuery object to poll

        :param condition: A callable that takes an ImageQuery and returns True or False
            whether to keep waiting for a better result.

        :param timeout_sec: The maximum number of seconds to wait.

        :return: ImageQuery
        """
        if isinstance(image_query, str):
            image_query = self.get_image_query(image_query)

        start_time = time.time()
        next_delay = self.POLLING_INITIAL_DELAY
        target_delay = 0.0
        image_query = self._fixup_image_query(image_query)
        while True:
            patience_so_far = time.time() - start_time
            if condition(image_query):
                logger.debug(f"Answer for {image_query} after {patience_so_far:.1f}s")
                break
            if patience_so_far >= timeout_sec:
                logger.debug(f"Timeout after {timeout_sec:.0f}s waiting for {image_query}")
                break
            target_delay = min(patience_so_far + next_delay, timeout_sec)
            sleep_time = max(target_delay - patience_so_far, 0)
            logger.debug(f"Polling ({target_delay:.1f}/{timeout_sec:.0f}s) {image_query} until result is available")
            time.sleep(sleep_time)
            next_delay *= self.POLLING_EXPONENTIAL_BACKOFF
            image_query = self.get_image_query(image_query.id)
            image_query = self._fixup_image_query(image_query)
        return image_query

    def add_label(self, image_query: Union[ImageQuery, str], label: Union[Label, str]):
        """
        Add a new label to an image query.  This answers the detector's question.

        :param image_query: Either an ImageQuery object (returned from `submit_image_query`)
                            or an image_query id as a string.

        :param label: The string "YES" or the string "NO" in answer to the query.

        :return: None
        """
        if isinstance(image_query, ImageQuery):
            image_query_id = image_query.id
        else:
            image_query_id = str(image_query)
            # Some old imagequery id's started with "chk_"
            # TODO: handle iqe_ for image_queries returned from edge endpoints
            if not image_query_id.startswith(("chk_", "iq_")):
                raise ValueError(f"Invalid image query id {image_query_id}")
        api_label = convert_display_label_to_internal(image_query_id, label)

        return self.api_client._add_label(image_query_id, api_label)  # pylint: disable=protected-access

    def start_inspection(self) -> str:
        """
        **NOTE:** For users with Inspection Reports enabled only.
        Starts an inspection report and returns the id of the inspection.

        :return: The unique identifier of the inspection.
        """
        return self.api_client.start_inspection()

    def update_inspection_metadata(self, inspection_id: str, user_provided_key: str, user_provided_value: str) -> None:
        """
        **NOTE:** For users with Inspection Reports enabled only.
        Add/update inspection metadata with the user_provided_key and user_provided_value.

        :param inspection_id: The unique identifier of the inspection.

        :param user_provided_key: the key in the key/value pair for the inspection metadata.

        :param user_provided_value: the value in the key/value pair for the inspection metadata.

        :return: None
        """
        self.api_client.update_inspection_metadata(inspection_id, user_provided_key, user_provided_value)

    def stop_inspection(self, inspection_id: str) -> str:
        """
        **NOTE:** For users with Inspection Reports enabled only.
        Stops an inspection and raises an exception if the response from the server
        indicates that the inspection was not successfully stopped.

        :param inspection_id: The unique identifier of the inspection.

        :return: "PASS" or "FAIL" depending on the result of the inspection.
        """
        return self.api_client.stop_inspection(inspection_id)

    def update_detector_confidence_threshold(self, detector_id: str, confidence_threshold: float) -> None:
        """
        Updates the confidence threshold of a detector given a detector_id.

        :param detector_id: The id of the detector to update.

        :param confidence_threshold: The new confidence threshold for the detector.

        :return None
        :rtype None
        """
        self.api_client.update_detector_confidence_threshold(detector_id, confidence_threshold)
