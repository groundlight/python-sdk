# pylint: disable=too-many-lines
import logging
import os
import time
import warnings
from functools import partial
from io import BufferedReader, BytesIO
from typing import Callable, List, Optional, Union

from groundlight_openapi_client import Configuration
from groundlight_openapi_client.api.detectors_api import DetectorsApi
from groundlight_openapi_client.api.image_queries_api import ImageQueriesApi
from groundlight_openapi_client.api.labels_api import LabelsApi
from groundlight_openapi_client.api.user_api import UserApi
from groundlight_openapi_client.exceptions import NotFoundException, UnauthorizedException
from groundlight_openapi_client.model.detector_creation_input_request import DetectorCreationInputRequest
from groundlight_openapi_client.model.label_value_request import LabelValueRequest
from groundlight_openapi_client.model.patched_detector_request import PatchedDetectorRequest
from model import (
    ROI,
    BinaryClassificationResult,
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


class Groundlight:  # pylint: disable=too-many-instance-attributes
    """
    Client for accessing the Groundlight cloud service. Provides methods to create visual detectors,
    submit images for analysis, and retrieve predictions.

    The API token (auth) is specified through the **GROUNDLIGHT_API_TOKEN** environment variable by default.

    **Example usage**::

        gl = Groundlight()
        detector = gl.get_or_create_detector(
            name="door_detector",
            query="Is the door open?",
            confidence_threshold=0.9
        )

        # Submit image and get prediction
        image_query = gl.submit_image_query(
            detector=detector,
            image="path/to/image.jpg",
            wait=30.0
        )
        print(f"Answer: {image_query.result.label}")

        # Async submission with human review
        image_query = gl.ask_async(
            detector=detector,
            image="path/to/image.jpg",
            human_review="ALWAYS"
        )

        # Later, get the result
        image_query = gl.wait_for_confident_result(
            image_query=image_query,
            confidence_threshold=0.95,
            timeout_sec=60.0
        )

    :param endpoint: Optional custom API endpoint URL. If not specified, uses the default Groundlight endpoint.
    :param api_token: Authentication token for API access. If not provided, will attempt to read from
            the "GROUNDLIGHT_API_TOKEN" environment variable.
    :param disable_tls_verification: If True, disables SSL/TLS certificate verification for API calls.
            When not specified, checks the "DISABLE_TLS_VERIFY" environment variable (1=disable, 0=enable).
            Certificate verification is enabled by default.

            Warning: Only disable verification when connecting to a Groundlight Edge Endpoint using
            self-signed certificates. For security, always keep verification enabled when using the
            Groundlight cloud service.

    :return: Groundlight client instance
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
    ):
        """
        Initialize a new Groundlight client instance.

        :param endpoint: Optional custom API endpoint URL. If not specified, uses the default Groundlight endpoint.
        :param api_token: Authentication token for API access.
                        If not provided, will attempt to read from the "GROUNDLIGHT_API_TOKEN" environment variable.
        :param disable_tls_verification: If True, disables SSL/TLS certificate verification for API calls.
                                       When not specified, checks the "DISABLE_TLS_VERIFY" environment variable
                                       (1=disable, 0=enable). Certificate verification is enabled by default.

                                       Warning: Only disable verification when connecting to a Groundlight Edge
                                       Endpoint using self-signed certificates. For security, always keep
                                       verification enabled when using the Groundlight cloud service.

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
        self.labels_api = LabelsApi(self.api_client)
        self.logged_in_user = "(not-logged-in)"
        self._verify_connectivity()

    def __repr__(self) -> str:
        # Don't call the API here because that can get us stuck in a loop rendering exception strings
        return f"Logged in as {self.logged_in_user} to Groundlight at {self.endpoint}"

    def _verify_connectivity(self) -> None:
        """
        Verify that the client can connect to the Groundlight service, and raise a helpful
        exception if it cannot.
        """
        try:
            # a simple query to confirm that the endpoint & API token are working
            self.logged_in_user = self.whoami()
            if self._user_is_privileged():
                logger.warning(
                    "WARNING: The current user has elevated permissions. Please verify such permissions are necessary"
                    " for your current operation"
                )
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
        if isinstance(iq.result, BinaryClassificationResult):
            iq.result.label = convert_internal_label_to_display(iq, iq.result.label)
        return iq

    def whoami(self) -> str:
        """
        Return the username (email address) associated with the current API token.

        This method verifies that the API token is valid and returns the email address of the authenticated user.
        It can be used to confirm that authentication is working correctly.

        **Example usage**::

            gl = Groundlight()
            username = gl.whoami()
            print(f"Authenticated as {username}")

        :return: The email address of the authenticated user
        :raises ApiTokenError: If the API token is invalid
        :raises GroundlightClientError: If there are connectivity issues with the Groundlight service
        """
        obj = self.user_api.who_am_i(_request_timeout=DEFAULT_REQUEST_TIMEOUT)
        return obj["email"]

    def _user_is_privileged(self) -> bool:
        """
        Return a boolean indicating whether the user is privileged.
        Privleged users have elevated permissions, so care should be taken when using a privileged account.
        """
        obj = self.user_api.who_am_i()
        return obj["is_superuser"]

    def get_detector(self, id: Union[str, Detector]) -> Detector:  # pylint: disable=redefined-builtin
        """
        Get a Detector by id.

        **Example usage**::

            gl = Groundlight()
            detector = gl.get_detector(id="det_12345")
            print(detector)

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
        Get a Detector by name.

        **Example usage**::

            gl = Groundlight()
            detector = gl.get_detector_by_name(name="door_detector")
            print(detector)

        :param name: the detector name

        :return: Detector
        """
        return self.api_client._get_detector_by_name(name)  # pylint: disable=protected-access

    def list_detectors(self, page: int = 1, page_size: int = 10) -> PaginatedDetectorList:
        """
        Retrieve a paginated list of detectors associated with your account.

        **Example usage**::

            gl = Groundlight()

            # Get first page of 5 detectors
            detectors = gl.list_detectors(page=1, page_size=5)

            for detector in detectors.items:
                print(detector)

        :param page: The page number to retrieve (1-based indexing). Use this parameter to navigate
            through multiple pages of detectors.
        :param page_size: The number of detectors to return per page.

        :return: PaginatedDetectorList containing the requested page of detectors and pagination metadata
        """
        obj = self.detectors_api.list_detectors(
            page=page, page_size=page_size, _request_timeout=DEFAULT_REQUEST_TIMEOUT
        )
        return PaginatedDetectorList.parse_obj(obj.to_dict())

    def _prep_create_detector(  # noqa: PLR0913 # pylint: disable=too-many-arguments, too-many-locals
        self,
        name: str,
        query: str,
        *,
        group_name: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
        patience_time: Optional[float] = None,
        pipeline_config: Optional[str] = None,
        metadata: Union[dict, str, None] = None,
    ) -> Detector:
        """
        A helper function to prepare the input for creating a detector. Individual create_detector
        methods may add to the input before calling the API.
        """
        detector_creation_input = DetectorCreationInputRequest(
            name=name,
            query=query,
            pipeline_config=pipeline_config,
        )
        if group_name is not None:
            detector_creation_input.group_name = group_name
        if metadata is not None:
            detector_creation_input.metadata = str(url_encode_dict(metadata, name="metadata", size_limit_bytes=1024))
        if confidence_threshold:
            detector_creation_input.confidence_threshold = confidence_threshold
        if isinstance(patience_time, int):
            patience_time = float(patience_time)
        if patience_time:
            detector_creation_input.patience_time = patience_time
        return detector_creation_input

    def create_detector(  # noqa: PLR0913
        self,
        name: str,
        query: str,
        *,
        group_name: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
        patience_time: Optional[float] = None,
        pipeline_config: Optional[str] = None,
        metadata: Union[dict, str, None] = None,
    ) -> Detector:
        """
        Create a new Detector with a given name and query.

        **Example usage**::

            gl = Groundlight()

            # Create a basic binary detector
            detector = gl.create_detector(
                name="dog-on-couch-detector",
                query="Is there a dog on the couch?",
                confidence_threshold=0.9,
                patience_time=30.0
            )

            # Create a detector with metadata
            detector = gl.create_detector(
                name="door-monitor",
                query="Is the door open?",
                metadata={"location": "front-entrance", "building": "HQ"},
                confidence_threshold=0.95
            )

            # Create a detector in a specific group
            detector = gl.create_detector(
                name="vehicle-counter",
                query="How many vehicles are in the parking lot?",
                group_name="parking-monitoring",
                patience_time=60.0
            )
        :param name: A short, descriptive name for the detector. This name should be unique within your account
                    and help identify the detector's purpose.
        :param query: The question that the detector will answer about images. For binary classification,
                     this should be a yes/no question (e.g. "Is there a person in the image?").
        :param group_name: Optional name of a group to organize related detectors together. If not specified,
                         the detector will be placed in the default group.
        :param confidence_threshold: A value between 0.5 and 1 that sets the minimum confidence level required
                                  for the ML model's predictions. If confidence is below this threshold,
                                  the query may be sent for human review.
        :param patience_time: The maximum time in seconds that Groundlight will attempt to generate a
                            confident prediction before falling back to human review. Defaults to 30 seconds.
        :param pipeline_config: Advanced usage only. Configuration string needed to instantiate a specific
                              prediction pipeline for this detector.
        :param metadata: A dictionary or JSON string containing custom key/value pairs to associate with
                        the detector (limited to 1KB). This metadata can be used to store additional
                        information like location, purpose, or related system IDs. You can retrieve this
                        metadata later by calling `get_detector()`.

        :return: The created Detector object
        """

        detector_creation_input = self._prep_create_detector(
            name=name,
            query=query,
            group_name=group_name,
            confidence_threshold=confidence_threshold,
            patience_time=patience_time,
            pipeline_config=pipeline_config,
            metadata=metadata,
        )
        obj = self.detectors_api.create_detector(detector_creation_input, _request_timeout=DEFAULT_REQUEST_TIMEOUT)
        return Detector.parse_obj(obj.to_dict())

    def get_or_create_detector(  # noqa: PLR0913
        self,
        name: str,
        query: str,
        *,
        group_name: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
        pipeline_config: Optional[str] = None,
        metadata: Union[dict, str, None] = None,
    ) -> Detector:
        """
        Tries to look up the Detector by name. If a Detector with that name, query, and
        confidence exists, return it. Otherwise, create a Detector with the specified query and
        config.

        **Example usage**::

            gl = Groundlight()

            detector = gl.get_or_create_detector(
                name="service-counter-usage",
                query="Is there a customer at the service counter?",
                group_name="retail-analytics",
                confidence_threshold=0.95,
                metadata={"location": "store-123"}
            )

        :param name: A short, descriptive name for the detector. This name should be unique within your account
                    and help identify the detector's purpose.
        :param query: The question that the detector will answer about images. For binary classification,
                     this should be a yes/no question (e.g. "Is there a person in the image?").
        :param group_name: Optional name of a group to organize related detectors together. If not specified,
                         the detector will be placed in the default group.
        :param confidence_threshold: A value between 0.5 and 1 that sets the minimum confidence level required
                                  for the ML model's predictions. If confidence is below this threshold,
                                  the query may be sent for human review.
        :param pipeline_config: Advanced usage only. Configuration string needed to instantiate a specific
                              prediction pipeline for this detector.
        :param metadata: A dictionary or JSON string containing custom key/value pairs to associate with
                        the detector (limited to 1KB). This metadata can be used to store additional
                        information like location, purpose, or related system IDs. You can retrieve this
                        metadata later by calling `get_detector()`.

        :return: Detector with the specified configuration
        :raises ValueError: If an existing detector is found but has different configuration
        :raises ApiTokenError: If API token is invalid
        :raises GroundlightClientError: For other API errors

        .. note::
            If a detector with the given name exists, this method verifies that its
            configuration (query, group_name, etc.) matches what was requested. If
            there are any mismatches, it raises ValueError rather than modifying the
            existing detector.
        """
        try:
            existing_detector = self.get_detector_by_name(name)
        except NotFoundError:
            logger.debug(f"We could not find a detector with name='{name}'. So we will create a new detector ...")
            return self.create_detector(
                name=name,
                query=query,
                group_name=group_name,
                confidence_threshold=confidence_threshold,
                pipeline_config=pipeline_config,
                metadata=metadata,
            )

        # TODO: We may soon allow users to update the retrieved detector's fields.
        if existing_detector.query != query:
            raise ValueError(
                f"Found existing detector with name={name} (id={existing_detector.id}) but the queries don't match."
                f" The existing query is '{existing_detector.query}'.",
            )
        if group_name is not None and existing_detector.group_name != group_name:
            raise ValueError(
                f"Found existing detector with name={name} (id={existing_detector.id}) but the group names don't"
                f" match. The existing group name is '{existing_detector.group_name}'.",
            )
        if confidence_threshold is not None and existing_detector.confidence_threshold != confidence_threshold:
            raise ValueError(
                f"Found existing detector with name={name} (id={existing_detector.id}) but the confidence"
                " thresholds don't match. The existing confidence threshold is"
                f" {existing_detector.confidence_threshold}.",
            )
        return existing_detector

    def get_image_query(self, id: str) -> ImageQuery:  # pylint: disable=redefined-builtin
        """
        Get an ImageQuery by its ID. This is useful for retrieving the status and results of a
        previously submitted query.

        **Example Usage:**

            gl = Groundlight()

            # Get an existing image query by ID
            image_query = gl.get_image_query("iq_abc123")

            # Get the result if available
            if image_query.result is not None:
                print(f"Answer: {image_query.result.label}")
                print(f"Source: {image_query.result.source}")
                print(f"Confidence: {image_query.result.confidence}")  # e.g. 0.98

        :param id: The ImageQuery ID to look up. This ID is returned when submitting a new ImageQuery.

        :return: ImageQuery object containing the query details and results
        """
        obj = self.image_queries_api.get_image_query(id=id, _request_timeout=DEFAULT_REQUEST_TIMEOUT)
        iq = ImageQuery.parse_obj(obj.to_dict())
        return self._fixup_image_query(iq)

    def list_image_queries(self, page: int = 1, page_size: int = 10) -> PaginatedImageQueryList:
        """
        List all image queries associated with your account, with pagination support.

        **Example Usage**::

            gl = Groundlight()

            # Get first page of 10 image queries
            queries = gl.list_image_queries(page=1, page_size=10)

            # Access results
            for query in queries.results:
                print(f"Query ID: {query.id}")
                print(f"Result: {query.result.label if query.result else 'No result yet'}")

        :param page: The page number to retrieve (1-based indexing). Use this parameter to navigate
            through multiple pages of image queries.
        :param page_size: Number of image queries to return per page. Default is 10.
        :return: PaginatedImageQueryList containing the requested page of image queries and pagination metadata
                like total count and links to next/previous pages.
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
        image_query_id: Optional[str] = None,
    ) -> ImageQuery:
        """
        Evaluates an image with Groundlight. This is the core method for getting predictions about images.

        **Example Usage**::

            from groundlight import Groundlight
            from PIL import Image

            gl = Groundlight()
            det = gl.get_or_create_detector(
                name="parking-space",
                query="Is there a car in the leftmost parking space?"
            )

            # Basic synchronous usage
            image = "path/to/image.jpg"
            image_query = gl.submit_image_query(detector=det, image=image)
            print(f"The answer is {image_query.result.label}")

            # Asynchronous usage with custom confidence
            image = Image.open("path/to/image.jpg")
            image_query = gl.submit_image_query(
                detector=det,
                image=image,
                wait=0,  # Don't wait for result
                confidence_threshold=0.95,
                want_async=True
            )
            print(f"Submitted image_query {image_query.id}")

            # With metadata and mandatory human review
            image_query = gl.submit_image_query(
                detector=det,
                image=image,
                metadata={"location": "entrance", "camera": "cam1"},
                human_review="ALWAYS"
            )

        .. note::
            This method supports both synchronous and asynchronous workflows, configurable confidence thresholds,
            and optional human review.

        .. seealso::
            :meth:`ask_confident` for a simpler synchronous workflow

            :meth:`ask_async` for a simpler asynchronous workflow

            :meth:`ask_ml` for faster ML predictions without waiting for a confident answer

        :param detector: the Detector object, or string id of a detector like `det_12345`
        :param image: The image, in several possible formats:
            - filename (string) of a jpeg file
            - byte array or BytesIO or BufferedReader with jpeg bytes
            - numpy array with values 0-255 and dimensions (H,W,3) in BGR order
                (Note OpenCV uses BGR not RGB. `img[:, :, ::-1]` will reverse the channels)
            - PIL Image: Any binary format must be JPEG-encoded already.
                Any pixel format will get converted to JPEG at high quality before sending to service.
        :param wait: How long to poll (in seconds) for a confident answer. This is a client-side timeout.
            Default is 30.0. Set to 0 for async operation.
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
        :param want_async: If True, return immediately without waiting for result.
                        Must set `wait=0` when using this option.
        :param inspection_id: Most users will omit this. For accounts with Inspection Reports enabled,
                           this is the ID of the inspection to associate with the image query.
        :param metadata: A dictionary or JSON string of custom key/value metadata to associate with
                      the image query (limited to 1KB). You can retrieve this metadata later by calling
                      `get_image_query()`.
        :param image_query_id: The ID for the image query. This is to enable specific functionality
                            and is not intended for general external use. If not set, a random ID
                            will be generated.

        :return: ImageQuery with query details and result (if wait > 0)
        :raises ValueError: If wait > 0 when want_async=True
        :raises ApiTokenError: If API token is invalid
        :raises GroundlightClientError: For other API errors
        """
        if wait is None:
            wait = self.DEFAULT_WAIT

        detector_id = detector.id if isinstance(detector, Detector) else detector

        image_bytesio: ByteStreamWrapper = parse_supported_image_types(image)

        params = {"detector_id": detector_id, "body": image_bytesio, "_request_timeout": DEFAULT_REQUEST_TIMEOUT}

        if patience_time is not None:
            params["patience_time"] = patience_time

        if confidence_threshold is not None:
            params["confidence_threshold"] = confidence_threshold

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

        if image_query_id is not None:
            params["image_query_id"] = image_query_id

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
        Evaluates an image with Groundlight, waiting until an answer above the confidence threshold
        is reached or the wait period has passed.

        **Example usage**::

            gl = Groundlight()
            image_query = gl.ask_confident(
                detector="det_12345",
                image="path/to/image.jpg",
                confidence_threshold=0.9,
                wait=30.0
            )
            if image_query.result.confidence >= 0.9:
                print(f"Confident answer: {image_query.result.label}")
            else:
                print("Could not get confident answer within timeout")

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
        :param inspection_id: Most users will omit this. For accounts with Inspection Reports enabled,
                           this is the ID of the inspection to associate with the image query.

        :return: ImageQuery containing the prediction result
        :raises ApiTokenError: If API token is invalid
        :raises GroundlightClientError: For other API errors

        .. seealso::
            :meth:`ask_ml` for getting the first ML prediction without waiting an answer above the confidence threshold
            :meth:`ask_async` for submitting queries asynchronously
            :meth:`submit_image_query` for submitting queries with more control over the process

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
        Evaluates an image with Groundlight, getting the first ML prediction without waiting
        for high confidence or human review.

        **Example usage**::

            gl = Groundlight()
            detector = gl.get_detector("det_12345")  # or create one with create_detector()

            # Get quick ML prediction for an image
            image_query = gl.ask_ml(detector, "path/to/image.jpg")

            # The image_query may have low confidence since we're never waiting for human review
            print(f"Quick ML prediction: {image_query.result.label}")
            print(f"Confidence: {image_query.result.confidence}")

            # You can also pass metadata to track additional information
            image_query = gl.ask_ml(
                detector=detector,
                image="path/to/image.jpg",
                metadata={"camera_id": "front_door", "timestamp": "2023-01-01T12:00:00Z"}
            )

        :param detector: the Detector object, or string id of a detector like `det_12345`
        :param image: The image, in several possible formats:
          - filename (string) of a jpeg file
          - byte array or BytesIO or BufferedReader with jpeg bytes
          - numpy array with values 0-255 and dimensions (H,W,3) in BGR order
            (Note OpenCV uses BGR not RGB. `img[:, :, ::-1]` will reverse the channels)
          - PIL Image
          Any binary format must be JPEG-encoded already.  Any pixel format will get
          converted to JPEG at high quality before sending to service.
        :param wait: How long to wait (in seconds) for any ML prediction.
                   Default is 30.0 seconds.
        :param metadata: A dictionary or JSON string of custom key/value metadata to associate with
            the image query (limited to 1KB). You can retrieve this metadata later by calling
            `get_image_query()`.
        :param inspection_id: Most users will omit this. For accounts with Inspection Reports enabled,
                           this is the ID of the inspection to associate with the image query.

        :return: ImageQuery containing the ML prediction
        :raises ApiTokenError: If API token is invalid
        :raises GroundlightClientError: For other API errors

        .. note::
            This method returns the first available ML prediction, which may have low confidence.
            For answers above a configured confidence_threshold, use :meth:`ask_confident` instead.

        .. seealso::
            :meth:`ask_confident` for waiting until a high-confidence prediction is available
            :meth:`ask_async` for submitting queries asynchronously
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
        Submit an image query asynchronously. This is equivalent to calling `submit_image_query`
        with `want_async=True` and `wait=0`.

        .. note::
            The returned ImageQuery will have result=None since the prediction is computed
            asynchronously. Use :meth:`wait_for_confident_result`, :meth:`wait_for_ml_result`,
            or :meth:`get_image_query` to retrieve the result later.

        **Example usage**::

            gl = Groundlight()

            # Submit query asynchronously
            image_query = gl.ask_async(
                detector="det_12345",
                image="path/to/image.jpg",
                confidence_threshold=0.9,
                human_review="ALWAYS"
            )
            print(f"Query submitted with ID: {query.id}")

            # Later, retrieve the result
            image_query = gl.wait_for_confident_result(
                image_query=query,
                confidence_threshold=0.9,
                timeout_sec=60.0
            )
            print(f"Answer: {image_query.result.label}")

            # Alternatively, check if result is ready without blocking
            image_query = gl.get_image_query(image_query.id)
            if image_query.result:
                print(f"Result ready: {image_query.result.label}")
            else:
                print("Still processing...")

        :param detector: the Detector object, or string id of a detector like `det_12345`
        :param image: The image, in several possible formats:
            - filename (string) of a jpeg file
            - byte array or BytesIO or BufferedReader with jpeg bytes
            - numpy array with values 0-255 and dimensions (H,W,3) in BGR order
              (Note OpenCV uses BGR not RGB. `img[:, :, ::-1]` will reverse the channels)
            - PIL Image: Any binary format must be JPEG-encoded already.
              Any pixel format will get converted to JPEG at high quality before sending to service.
        :param patience_time: How long to wait (in seconds) for a confident answer for this image query.
            The longer the patience_time, the more likely Groundlight will arrive at a
            confident answer. This is a soft server-side timeout. If not set, use the
            detector's patience_time.
        :param confidence_threshold: The confidence threshold to wait for.
            If not set, use the detector's confidence threshold.
        :param human_review: If `None` or `DEFAULT`, send the image query for human review
            only if the ML prediction is not confident.
            If set to `ALWAYS`, always send the image query for human review.
            If set to `NEVER`, never send the image query for human review.
        :param metadata: A dictionary or JSON string of custom key/value metadata to associate with
            the image query (limited to 1KB). You can retrieve this metadata later by calling
            `get_image_query()`.
        :param inspection_id: Most users will omit this. For accounts with Inspection Reports enabled,
            this is the ID of the inspection to associate with the image query.

        :return: ImageQuery with result set to None (result will be computed asynchronously)
        :raises ApiTokenError: If API token is invalid
        :raises GroundlightClientError: For other API errors

        .. seealso::
            :meth:`wait_for_confident_result` for waiting until a confident result is available
            :meth:`wait_for_ml_result` for waiting until the first ML result is available
            :meth:`get_image_query` for checking if a result is ready without blocking
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
        Waits for an image query result's confidence level to reach the specified confidence_threshold.
        Uses polling with exponential back-off to check for results.

        .. note::
            This method blocks until either:
            1. A result with confidence >= confidence_threshold is available
            2. The timeout_sec is reached
            3. An error occurs

        **Example usage**::

            gl = Groundlight()
            query = gl.ask_async(
                            detector="det_12345",
                            image="path/to/image.jpg"
                        )
            try:
                result = gl.wait_for_confident_result(
                                query,
                                confidence_threshold=0.9,
                                timeout_sec=60.0
                            )
                print(f"Got confident answer: {result.result.label}")
            except TimeoutError:
                print("Timed out waiting for confident result")

        :param image_query: An ImageQuery object or query ID string to poll
        :param confidence_threshold: The confidence threshold to wait for.
                                  If not set, use the detector's confidence threshold.
        :param timeout_sec: The maximum number of seconds to wait. Default is 30.0 seconds.

        :return: ImageQuery with confident result
        :raises TimeoutError: If no confident result is available within timeout_sec
        :raises ApiTokenError: If API token is invalid
        :raises GroundlightClientError: For other API errors

        .. seealso::
            :meth:`ask_async` for submitting queries asynchronously
            :meth:`get_image_query` for checking result status without blocking
            :meth:`wait_for_ml_result` for waiting until the first ML result is available
        """
        if isinstance(image_query, str):
            image_query = self.get_image_query(image_query)
            confidence_threshold = self.get_detector(image_query.detector_id).confidence_threshold

        confidence_above_thresh = partial(iq_is_confident, confidence_threshold=confidence_threshold)  # type: ignore
        return self._wait_for_result(image_query, condition=confidence_above_thresh, timeout_sec=timeout_sec)

    def wait_for_ml_result(self, image_query: Union[ImageQuery, str], timeout_sec: float = 30.0) -> ImageQuery:
        """
        Waits for the first ML result to be returned for an image query.
        Uses polling with exponential back-off to check for results.

        .. note::
            This method blocks until either:
            1. An ML result is available
            2. The timeout_sec is reached
            3. An error occurs

        **Example usage**::

            gl = Groundlight()
            query = gl.ask_async(
                detector="det_12345",
                image="path/to/image.jpg"
            )

            try:
                result = gl.wait_for_ml_result(query, timeout_sec=3.0)
                print(f"Got ML result: {result.result.label}")
            except TimeoutError:
                print("Timed out waiting for ML result")

        :param image_query: An ImageQuery object or ImageQuery ID string to poll
        :param timeout_sec: The maximum number of seconds to wait. Default is 30.0 seconds.

        :return: ImageQuery with ML result
        :raises TimeoutError: If no ML result is available within timeout_sec
        :raises ApiTokenError: If API token is invalid
        :raises GroundlightClientError: For other API errors

        .. seealso::
            :meth:`ask_async` for submitting queries asynchronously
            :meth:`get_image_query` for checking result status without blocking
            :meth:`wait_for_confident_result` for waiting until a confident result is available
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

    def add_label(
        self, image_query: Union[ImageQuery, str], label: Union[Label, str], rois: Union[List[ROI], str, None] = None
    ):
        """
        Provide a new label (annotation) for an image query. This is used to provide ground-truth labels
        for training detectors, or to correct the results of detectors.

        **Example usage**::

            gl = Groundlight()

            # Using an ImageQuery object
            image_query = gl.ask_ml(detector_id, image_data)
            gl.add_label(image_query, "YES")

            # Using an image query ID string directly
            gl.add_label("iq_abc123", "NO")

            # With regions of interest (ROIs)
            rois = [ROI(x=100, y=100, width=50, height=50)]
            gl.add_label(image_query, "YES", rois=rois)

        :param image_query: Either an ImageQuery object (returned from methods like :meth:`ask_ml`) or an image query ID
            string starting with "iq_".
        :param label: The label value to assign, typically "YES" or "NO" for binary classification detectors.
            For multi-class detectors, use one of the defined class names.
        :param rois: Optional list of ROI objects defining regions of interest in the image.
            Each ROI specifies a bounding box with x, y coordinates and width, height.

        :return: None
        """
        if isinstance(rois, str):
            raise TypeError("rois must be a list of ROI objects. CLI support is not implemented")
        if isinstance(image_query, ImageQuery):
            image_query_id = image_query.id
        else:
            image_query_id = str(image_query)
            # Some old imagequery id's started with "chk_"
            if not image_query_id.startswith(("chk_", "iq_")):
                raise ValueError(f"Invalid image query id {image_query_id}")
        api_label = convert_display_label_to_internal(image_query_id, label)
        rois_json = [roi.dict() for roi in rois] if rois else None
        request_params = LabelValueRequest(label=api_label, image_query_id=image_query_id, rois=rois_json)
        self.labels_api.create_label(request_params)

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

    def update_detector_confidence_threshold(self, detector: Union[str, Detector], confidence_threshold: float) -> None:
        """
        Updates the confidence threshold for the given detector

        :param detector: the detector to update
        :param confidence_threshold: the new confidence threshold

        :return: None
        """
        if isinstance(detector, Detector):
            detector = detector.id
        if confidence_threshold < 0 or confidence_threshold > 1:
            raise ValueError("confidence must be between 0 and 1")
        self.detectors_api.update_detector(
            detector, patched_detector_request=PatchedDetectorRequest(confidence_threshold=confidence_threshold)
        )
