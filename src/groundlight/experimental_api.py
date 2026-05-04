# pylint: disable=too-many-lines
"""
experimental_api.py

This module is part of our evolving SDK. While these functions are designed to provide valuable functionality to enhance
your projects, it's important to note that they are considered unstable. This means they may undergo significant
modifications or potentially be removed in future releases, which could lead to breaking changes in your applications.
"""

from http import HTTPStatus
from io import BufferedReader, BytesIO
from pathlib import Path
from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse, urlunparse

import requests
from groundlight_openapi_client.api.detector_groups_api import DetectorGroupsApi
from groundlight_openapi_client.api.detector_reset_api import DetectorResetApi
from groundlight_openapi_client.api.edge_api import EdgeApi
from groundlight_openapi_client.api.notes_api import NotesApi
from groundlight_openapi_client.api.priming_groups_api import PrimingGroupsApi
from groundlight_openapi_client.exceptions import ApiException, NotFoundException
from groundlight_openapi_client.model.patched_detector_request import PatchedDetectorRequest
from groundlight_openapi_client.model.priming_group_creation_input_request import PrimingGroupCreationInputRequest
from groundlight_openapi_client.model.text_mode_configuration import TextModeConfiguration
from model import (
    Detector,
    EdgeModelInfo,
    ModeEnum,
    PaginatedMLPipelineList,
    PaginatedPrimingGroupList,
    PrimingGroup,
)
from urllib3.response import HTTPResponse

from groundlight.edge.api import EdgeEndpointApi
from groundlight.images import parse_supported_image_types
from groundlight.internalapi import NotFoundError, _generate_request_id
from groundlight.optional_imports import Image, np

from .client import DEFAULT_REQUEST_TIMEOUT, Groundlight, GroundlightClientError


class ExperimentalApi(Groundlight):  # pylint: disable=too-many-public-methods,too-many-instance-attributes
    def __init__(
        self,
        endpoint: Union[str, None] = None,
        api_token: Union[str, None] = None,
        disable_tls_verification: Optional[bool] = None,
    ):
        """
        Constructs an experimental Groundlight client.

        This client extends the base Groundlight client with additional experimental functionality that is still in
        development. Note that experimental features may undergo significant changes or be removed in future releases.

        **Example usage**::

            from groundlight import ExperimentalApi

            # Create an experimental API client
            gl = ExperimentalApi()

            # Create a detector group
            group = gl.create_detector_group(
                name="Security Detectors",
                description="Detectors monitoring security-related conditions",
                detectors=["door_detector", "motion_detector"]
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
        """
        super().__init__(endpoint=endpoint, api_token=api_token, disable_tls_verification=disable_tls_verification)
        self.notes_api = NotesApi(self.api_client)
        self.detector_group_api = DetectorGroupsApi(self.api_client)
        self.detector_reset_api = DetectorResetApi(self.api_client)
        self.priming_groups_api = PrimingGroupsApi(self.api_client)

        # API client for fetching Edge models
        self._edge_model_download_api = EdgeApi(self.api_client)

        # API client for interacting with the EdgeEndpoint (getting/setting configuration, etc.)
        self.edge = EdgeEndpointApi(self)

    def get_notes(self, detector: Union[str, Detector]) -> Dict[str, Any]:
        """
        Retrieves all notes associated with a detector.

        **Example usage**::

            gl = ExperimentalApi()

            detector = gl.get_detector("det_123")
            notes = gl.get_notes(detector)
            # notes = {
            #     "CUSTOMER": ["Customer note 1", "Customer note 2"],
            #     "GL": ["Groundlight note 1"]
            # }

        :param detector: The detector object or ID string to retrieve notes for

        :return: A dictionary containing notes organized by source ("CUSTOMER" or "GL"),
            where each source maps to a list of note strings
        """
        det_id = detector.id if isinstance(detector, Detector) else detector
        return self.notes_api.get_notes(det_id)

    def create_note(
        self,
        detector: Union[str, Detector],
        note: str,
        image: Union[str, bytes, Image.Image, BytesIO, BufferedReader, np.ndarray, None] = None,
        is_pinned: bool = False,
    ) -> None:
        """
        Adds a note to a given detector.

        **Example usage**::

            gl = ExperimentalApi()

            detector = gl.get_detector("det_123")
            gl.create_note(detector, "Please label doors that are slightly ajar as 'YES'")

            # With an image attachment
            gl.create_note(
                detector,
                "Door that is slightly ajar and should be labeled 'YES'",
                image="path/to/image.jpg"
            )

        :param detector: The detector object or detector ID string to add the note to
        :param note: The text content of the note to add
        :param image: Optional image to attach to the note.
        """
        det_id = detector.id if isinstance(detector, Detector) else detector

        # Initialize img_bytes to None
        img_bytes = None
        if image is not None:
            img_bytes = parse_supported_image_types(image)

        # TODO: The openapi generator doesn't handle file submissions well at the moment, so we manually implement this
        # kwargs = {"image": img_bytes}
        # self.notes_api.create_note(det_id, note, **kwargs)
        url = f"{self.endpoint}/v1/notes"
        files = {"image": ("image.jpg", img_bytes, "image/jpeg")} if img_bytes is not None else None
        data = {
            "content": note,
            "is_pinned": is_pinned,
        }
        params = {"detector_id": det_id}
        headers = {"x-api-token": self.configuration.api_key["ApiToken"]}

        response = requests.post(url, headers=headers, data=data, files=files, params=params)  # type: ignore
        response.raise_for_status()  # Raise an exception for error status codes

    def reset_detector(self, detector: Union[str, Detector]) -> None:
        """
        Removes all image queries and training data for the given detector. This effectively resets
        the detector to its initial state, allowing you to start fresh with new training data.

        .. warning::
            This operation cannot be undone. All image queries and training data will be deleted.

        **Example usage**::

            gl = ExperimentalApi()

            # Using a detector object
            detector = gl.get_detector("det_abc123")
            gl.reset_detector(detector)

            # Using a detector ID string directly
            gl.reset_detector("det_abc123")

        :param detector: Either a Detector object or a detector ID string starting with "det_".
                       The detector whose data should be reset.

        :return: None
        """
        if isinstance(detector, Detector):
            detector = detector.id
        self.detector_reset_api.reset_detector(detector)

    def update_detector_name(self, detector: Union[str, Detector], name: str) -> None:
        """
        Updates the name of the given detector

        **Example usage**::

            gl = ExperimentalApi()

            # Using a detector object
            detector = gl.get_detector("det_abc123")
            gl.update_detector_name(detector, "new_detector_name")

            # Using a detector ID string directly
            gl.update_detector_name("det_abc123", "new_detector_name")

        :param detector: Either a Detector object or a detector ID string starting with "det_".
                       The detector whose name should be updated.
        :param name: The new name to assign to the detector

        :return: None
        """
        if isinstance(detector, Detector):
            detector = detector.id
        self.detectors_api.update_detector(detector, patched_detector_request=PatchedDetectorRequest(name=name))

    def create_text_recognition_detector(  # noqa: PLR0913 # pylint: disable=too-many-arguments, too-many-locals
        self,
        name: str,
        query: str,
        *,
        group_name: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
        patience_time: Optional[float] = None,
        pipeline_config: Optional[str] = None,
        edge_pipeline_config: Optional[str] = None,
        metadata: Union[dict, str, None] = None,
        priming_group_id: Optional[str] = None,
    ) -> Detector:
        """
        Creates a text recognition detector that can read specified spans of text from images.

        **Example usage**::

            gl = ExperimentalApi()

            # Create a text recognition detector
            detector = gl.create_text_recognition_detector(
                name="date_and_time_detector",
                query="Read the date and time from the bottom left corner of the image.",
            )

        :param name: A short, descriptive name for the detector.
        :param query: A question about the object to detect in the image.
        :param group_name: Optional name of a group to organize related detectors together.
        :param confidence_threshold: A value that sets the minimum confidence level required for the ML model's
                            predictions. If confidence is below this threshold, the query may be sent for human review.
        :param patience_time: The maximum time in seconds that Groundlight will attempt to generate a
                            confident prediction before falling back to human review. Defaults to 30 seconds.
        :param pipeline_config: Advanced usage only. Configuration string needed to instantiate a specific
                              prediction pipeline for this detector.
        :param edge_pipeline_config: Advanced usage only. Configuration for the edge inference pipeline.
                              If not specified, the mode's default edge pipeline is used.
        :param metadata: A dictionary or JSON string containing custom key/value pairs to associate with
                        the detector (limited to 1KB). This metadata can be used to store additional
                        information like location, purpose, or related system IDs. You can retrieve this
                        metadata later by calling `get_detector()`.
        :param priming_group_id: Optional ID of an existing PrimingGroup to associate with this detector.
                        You can create a PrimingGroup using the ExperimentalApi's create_priming_group method.

        :return: The created Detector object
        """

        detector_creation_input = self._prep_create_detector(
            name=name,
            query=query,
            group_name=group_name,
            confidence_threshold=confidence_threshold,
            patience_time=patience_time,
            pipeline_config=pipeline_config,
            edge_pipeline_config=edge_pipeline_config,
            metadata=metadata,
            priming_group_id=priming_group_id,
        )
        detector_creation_input.mode = ModeEnum.TEXT
        mode_config = TextModeConfiguration()

        detector_creation_input.mode_configuration = mode_config
        obj = self.detectors_api.create_detector(detector_creation_input, _request_timeout=DEFAULT_REQUEST_TIMEOUT)
        return Detector.model_validate(obj.to_dict())

    def _download_mlbinary_url(self, detector: Union[str, Detector]) -> EdgeModelInfo:
        """
        Gets a temporary presigned URL to download the model binaries for the given detector, along
        with relevant metadata
        """
        if isinstance(detector, Detector):
            detector = detector.id
        obj = self._edge_model_download_api.get_model_urls(detector)
        return EdgeModelInfo.model_validate(obj.to_dict())

    def download_mlbinary(self, detector: Union[str, Detector], output_dir: str) -> None:
        """
        Downloads the model binary files for the given detector to the specified output path.

        **Example usage**::

            gl = ExperimentalApi()

            # Download the model binary for a detector
            detector = gl.get_detector("det_abc123")
            gl.download_mlbinary(detector, "path/to/output/model.bin")

        :param detector: The detector object or detector ID string to download the model binary for.
        :param output_path: The path to save the model binary file to.

        :return: None
        """

        def _download_and_save(url: str, output_path: str) -> bytes:
            try:
                response = requests.get(url, timeout=10)
            except Exception as e:
                raise GroundlightClientError(f"Failed to retrieve data from {url}.") from e
            with open(output_path, "wb") as file:
                file.write(response.content)
            return response.content

        if isinstance(detector, Detector):
            detector = detector.id
        edge_model_info = self._download_mlbinary_url(detector)
        _download_and_save(edge_model_info.model_binary_url, Path(output_dir) / edge_model_info.model_binary_id)
        _download_and_save(
            edge_model_info.oodd_model_binary_url, Path(output_dir) / edge_model_info.oodd_model_binary_id
        )

    def get_detector_evaluation(self, detector: Union[str, Detector]) -> dict:
        """
        Get a specific evaluation for a detector

        :param detector: the detector to get the evaluation for

        :return: a dictionary containing the evaluation results
        """
        if isinstance(detector, Detector):
            detector = detector.id
        obj = self.detectors_api.get_detector_evaluation(detector)
        return obj.to_dict()

    def get_detector_metrics(self, detector: Union[str, Detector]) -> dict:
        """
        Get the metrics for a detector

        :param detector: the detector to get the metrics for

        :return: a dictionary containing the metrics for the detector
        """
        if isinstance(detector, Detector):
            detector = detector.id
        obj = self.detectors_api.get_detector_metrics(detector)
        return obj.to_dict()

    def get_raw_headers(self) -> dict:
        """
        Get the raw headers for the current API client

        :return: a dictionary containing the raw headers
        """
        headers = {}
        # see generated/groundlight_openapi_client/api_client.py update_params_for_auth
        headers["x-api-token"] = self.api_client.configuration.api_key["ApiToken"]
        # We generate a unique request ID client-side for each request
        headers["X-Request-Id"] = _generate_request_id()
        headers["User-Agent"] = self.api_client.default_headers["User-Agent"]
        headers["Accept"] = "application/json"
        return headers

    def make_generic_api_request(  # noqa: PLR0913 # pylint: disable=too-many-arguments
        self,
        *,
        endpoint: str,
        method: str,
        headers: Union[dict, None] = None,
        body: Union[dict, None] = None,
        files=None,
    ) -> HTTPResponse:
        """
        Make a generic API request to the specified endpoint, utilizing many of the provided tools
        from the generated api client

        :param endpoint: the endpoint to send the request to - the url path appended after the
            endpoint including a / at the beginging
        :param method: the HTTP method to use
        :param body: the request body

        :return: a dictionary containing the response
        """
        # HEADERS MUST BE THE 4TH ARGUMENT, 0 INDEXED
        if not headers:
            headers = self.get_raw_headers()
        return self.api_client.call_api(
            endpoint,
            method,
            None,  # Path Params
            None,  # Query params
            headers,  # header params
            body=body,  # body
            files=files,  # files
            auth_settings=["ApiToken"],
            _preload_content=False,  # This returns the urllib3 response rather than trying any type of processing
        )

    def edge_base_url(self) -> str:
        """Return the scheme+host+port of the configured endpoint, without the /device-api path."""
        parsed = urlparse(self.configuration.host)
        return urlunparse((parsed.scheme, parsed.netloc, "", "", "", ""))

    # ---------------------------------------------------------------------------
    # ML Pipeline methods
    # ---------------------------------------------------------------------------

    def list_detector_pipelines(
        self, detector: Union[str, Detector], page: int = 1, page_size: int = 10
    ) -> PaginatedMLPipelineList:
        """
        Lists all ML pipelines associated with a given detector.

        Each detector can have multiple pipelines (active, edge, shadow, etc.). This method returns
        all of them, which is useful when selecting a source pipeline to seed a new PrimingGroup.

        **Example usage**::

            gl = ExperimentalApi()
            detector = gl.get_detector("det_abc123")
            pipelines = gl.list_detector_pipelines(detector)
            for p in pipelines.results:
                if p.is_active_pipeline:
                    print(f"Active pipeline: {p.id}, config={p.pipeline_config}")

        :param detector: A Detector object or detector ID string.
        :param page: The page number to retrieve (1-based indexing).
        :param page_size: The number of pipelines to return per page.
        :return: PaginatedMLPipelineList containing the requested page of pipelines and pagination metadata.
        """
        detector_id = detector.id if isinstance(detector, Detector) else detector
        try:
            obj = self.detectors_api.list_detector_pipelines(detector_id, page=page, page_size=page_size)
            return PaginatedMLPipelineList.model_validate(obj.to_dict())
        except NotFoundException as e:
            raise NotFoundError(f"Detector '{detector_id}' not found.") from e

    # ---------------------------------------------------------------------------
    # PrimingGroup methods
    # ---------------------------------------------------------------------------

    def list_priming_groups(self, page: int = 1, page_size: int = 10) -> PaginatedPrimingGroupList:
        """
        Lists all PrimingGroups owned by the authenticated user's account.

        PrimingGroups let you seed new detectors with a pre-trained model so they start with a
        meaningful head start instead of a blank slate.

        **Example usage**::

            gl = ExperimentalApi()
            groups = gl.list_priming_groups()
            for g in groups.results:
                print(f"{g.name}: {g.id}")

        :param page: The page number to retrieve (1-based indexing).
        :param page_size: The number of priming groups to return per page.
        :return: PaginatedPrimingGroupList containing the requested page of priming groups and pagination metadata.
        """
        obj = self.priming_groups_api.list_priming_groups(page=page, page_size=page_size)
        return PaginatedPrimingGroupList.model_validate(obj.to_dict())

    def create_priming_group(
        self,
        name: str,
        source_ml_pipeline_id: str,
        canonical_query: Optional[str] = None,
        disable_shadow_pipelines: bool = False,
    ) -> PrimingGroup:
        """
        Creates a new PrimingGroup seeded from an existing ML pipeline.

        The trained model binary from the source pipeline is copied into the new PrimingGroup.
        Detectors subsequently created with this PrimingGroup's ID will start with that model
        already loaded, bypassing the cold-start period.

        **Example usage**::

            gl = ExperimentalApi()
            detector = gl.get_detector("det_abc123")
            pipelines = gl.list_detector_pipelines(detector)
            active = next(p for p in pipelines.results if p.is_active_pipeline)

            priming_group = gl.create_priming_group(
                name="door-detector-primer",
                source_ml_pipeline_id=active.id,
                canonical_query="Is the door open?",
                disable_shadow_pipelines=True,
            )
            print(f"Created priming group: {priming_group.id}")

        :param name: A short, descriptive name for the priming group.
        :param source_ml_pipeline_id: The ID of an MLPipeline whose trained model will seed this group.
                                      The pipeline must belong to a detector in your account.
        :param canonical_query: An optional description of the visual question this group answers.
        :param disable_shadow_pipelines: If True, detectors created in this group will not receive
                                         default shadow pipelines, ensuring the primed model stays active.
        :return: The created PrimingGroup object.
        """
        request = PrimingGroupCreationInputRequest(
            name=name,
            source_ml_pipeline_id=source_ml_pipeline_id,
            canonical_query=canonical_query,
            disable_shadow_pipelines=disable_shadow_pipelines,
        )
        result = self.priming_groups_api.create_priming_group(request)
        return PrimingGroup.model_validate(result.to_dict())

    def get_priming_group(self, priming_group_id: str) -> PrimingGroup:
        """
        Retrieves a PrimingGroup by ID.

        **Example usage**::

            gl = ExperimentalApi()
            pg = gl.get_priming_group("pg_abc123")
            print(f"Priming group name: {pg.name}")

        :param priming_group_id: The ID of the PrimingGroup to retrieve.
        :return: The PrimingGroup object.
        """
        try:
            result = self.priming_groups_api.get_priming_group(priming_group_id)
            return PrimingGroup.model_validate(result.to_dict())
        except NotFoundException as e:
            raise NotFoundError(f"PrimingGroup '{priming_group_id}' not found.") from e
        except ApiException as e:
            # Handle 410 Gone (soft-deleted priming groups)
            if e.status == HTTPStatus.GONE:
                raise NotFoundError(f"PrimingGroup '{priming_group_id}' has been deleted.") from e
            raise

    def delete_priming_group(self, priming_group_id: str) -> None:
        """
        Deletes (soft-deletes) a PrimingGroup owned by the authenticated user.

        This does not delete any detectors that were created using this priming group —
        it only removes the priming group itself. Detectors already created remain unaffected.

        **Example usage**::

            gl = ExperimentalApi()
            gl.delete_priming_group("pg_abc123")

        :param priming_group_id: The ID of the PrimingGroup to delete.
        """
        try:
            self.priming_groups_api.delete_priming_group(priming_group_id)
        except NotFoundException as e:
            raise NotFoundError(f"PrimingGroup '{priming_group_id}' not found.") from e
