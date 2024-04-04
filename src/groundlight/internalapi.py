import json
import logging
import os
import random
import time
import uuid
from enum import Enum
from functools import wraps
from typing import Callable, Optional
from urllib.parse import urlsplit, urlunsplit

import requests
from groundlight_openapi_client.api_client import ApiClient, ApiException
from model import Detector, ImageQuery

from groundlight.status_codes import is_ok
from groundlight.version import get_version

logger = logging.getLogger("groundlight.sdk")


class NotFoundError(Exception):
    pass


def sanitize_endpoint_url(endpoint: Optional[str] = None) -> str:
    """Takes a URL for an endpoint, and returns a "sanitized" version of it.
    Currently the production API path must be exactly "/device-api".
    This allows people to leave that off entirely, or add a trailing slash.
    Also some future-proofing by allowing "v1" or "v2" or "v3" paths.
    """
    if not endpoint:
        endpoint = os.environ.get("GROUNDLIGHT_ENDPOINT", "")
        if not endpoint:
            # Because sometimes people set an environment variable to a blank string by mistake
            endpoint = "https://api.groundlight.ai/"
    parts = urlsplit(endpoint)
    if (parts.scheme not in ("http", "https")) or (not parts.netloc):
        raise ValueError(
            (
                f"Invalid API endpoint {endpoint}.  Unsupported scheme: {parts.scheme}.  Must be http or https, e.g."
                " https://api.groundlight.ai/"
            ),
        )
    if parts.query or parts.fragment:
        raise ValueError(f"Invalid API endpoint {endpoint}.  Cannot have query or fragment.")
    if not parts.path:
        parts = parts._replace(path="/")
    if not parts.path.endswith("/"):
        parts = parts._replace(path=parts.path + "/")
    if parts.path == "/":
        parts = parts._replace(path="/device-api/")
    if parts.path not in ("/device-api/", "/v1/", "/v2/", "/v3/"):
        logger.warning(f"Configured endpoint {endpoint} does not look right - path '{parts.path}' seems wrong.")
    out = urlunsplit(parts)
    out = out[:-1]  # remove trailing slash
    return out


def _generate_request_id():
    return "req_uu" + uuid.uuid4().hex


def iq_is_confident(iq: ImageQuery, confidence_threshold: float) -> bool:
    """Returns True if the image query's confidence is above threshold.
    The only subtletie here is that currently confidence of None means
    human label, which is treated as confident.
    """
    if iq.result.confidence is None:
        # Human label
        return True
    return iq.result.confidence >= confidence_threshold


def iq_is_answered(iq: ImageQuery) -> bool:
    """Returns True if the image query has a ML or human label.
    Placeholder and special labels (out of domain) have confidences exactly 0.5
    """
    if iq.result.confidence is None:
        # Human label
        return True
    placeholder_confidence = 0.5
    return iq.result.confidence > placeholder_confidence


class InternalApiError(ApiException, RuntimeError):
    # TODO: We should really avoid this double inheritance since
    # both `ApiException` and `RuntimeError` are subclasses of
    # `Exception`. Error handling might become more complex since
    # the two super classes cross paths.
    # pylint: disable=useless-super-delegation
    def __init__(self, status=None, reason=None, http_resp=None):
        super().__init__(status, reason, http_resp)


class RequestsRetryDecorator:
    """
    Decorate a function to retry sending HTTP requests.

    Tries to re-execute the decorated function in case the execution
    fails due to a server error (HTTP Error code 500 - 599).
    Retry attempts are executed while exponentially backing off by a factor
    of 2 with full jitter (picking a random delay time between 0 and the
    maximum delay time).

    """

    def __init__(
        self,
        initial_delay: float = 0.2,
        exponential_backoff: int = 2,
        status_code_range: tuple = (500, 600),
        max_retries: int = 3,
    ):
        self.initial_delay = initial_delay
        self.exponential_backoff = exponential_backoff
        self.status_code_range = range(*status_code_range)
        self.max_retries = max_retries

    def __call__(self, function: Callable) -> Callable:
        """:param callable: The function to invoke."""

        @wraps(function)
        def decorated(*args, **kwargs):  # pylint: disable=inconsistent-return-statements
            delay = self.initial_delay
            retry_count = 0

            while retry_count <= self.max_retries:
                try:
                    return function(*args, **kwargs)
                except ApiException as e:
                    is_retryable = (e.status is not None) and (e.status in self.status_code_range)
                    if not is_retryable:
                        raise e
                    if retry_count == self.max_retries:
                        raise InternalApiError(reason="Maximum retries reached") from e

                    if is_retryable:
                        status_code = e.status
                        if status_code in self.status_code_range:
                            # This is implementing a full jitter strategy
                            random_delay = random.uniform(0, delay)
                            logger.warning(
                                (
                                    f"Current HTTP response status: {status_code}. "
                                    f"Remaining retries: {self.max_retries - retry_count}. "
                                    f"Delaying {random_delay:.1f}s before retrying."
                                ),
                                exc_info=True,
                            )
                            time.sleep(random_delay)

                retry_count += 1
                delay *= self.exponential_backoff

        return decorated


# ReviewReasons are reasons a label was created. A review reason is a required field when posting a human label
# to the API. The only review reason currently supported on the SDK is CUSTOMER_INITIATED.
class ReviewReason(str, Enum):  # noqa: N801
    CUSTOMER_INITIATED = "CUSTOMER_INITIATED"


class GroundlightApiClient(ApiClient):
    """Subclassing the OpenAPI-generated ApiClient to add a bit of custom functionality.
    Not crazy about using polymorphism, but this is simpler than modifying the moustache
    templates in the generator to add the functionality.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_agent = f"Groundlight-Python-SDK/{get_version()}"

    REQUEST_ID_HEADER = "X-Request-Id"

    @RequestsRetryDecorator()
    def call_api(self, *args, **kwargs):
        """Adds a request-id header to each API call."""
        # Note we don't look for header_param in kwargs here, because this method is only called in one place
        # in the generated code, so we can afford to make this brittle.
        header_param = args[4]  # that's the number in the list
        if not header_param:
            # This will never happen in normal usage.
            logger.warning("Can't set request-id because headers not set")
        elif not header_param.get(self.REQUEST_ID_HEADER, None):
            header_param[self.REQUEST_ID_HEADER] = _generate_request_id()
            # Note that we have updated the actual dict in args, so we don't have to put it back in
        return super().call_api(*args, **kwargs)

    #
    # The methods below will eventually go away when we move to properly model
    # these methods with OpenAPI
    #
    def _headers(self) -> dict:
        request_id = _generate_request_id()
        return {
            "Content-Type": "application/json",
            "x-api-token": self.configuration.api_key["ApiToken"],
            "X-Request-Id": request_id,
            # This metadata helps us debug issues with specific SDK versions.
            "x-sdk-version": get_version(),
            "x-sdk-language": "python",
            "User-Agent": self.user_agent,
        }

    @RequestsRetryDecorator()
    def _add_label(self, image_query_id: str, label: str) -> dict:
        """Temporary internal call to add a label to an image query.  Not supported."""
        # TODO: Properly model this with OpenApi spec.
        start_time = time.time()
        url = f"{self.configuration.host}/labels"

        data = {"label": label, "posicheck_id": image_query_id, "review_reason": ReviewReason.CUSTOMER_INITIATED}

        headers = self._headers()

        logger.info(f"Posting label={label} to image_query {image_query_id} ...")
        response = requests.request("POST", url, json=data, headers=headers, verify=self.configuration.verify_ssl)
        elapsed = 1000 * (time.time() - start_time)
        logger.debug(f"Call to ImageQuery.add_label took {elapsed:.1f}ms response={response.text}")

        if not is_ok(response.status_code):
            raise InternalApiError(
                status=response.status_code,
                reason=f"Error adding label to image query {image_query_id}",
                http_resp=response,
            )

        return response.json()

    @RequestsRetryDecorator()
    def _get_detector_by_name(self, name: str) -> Detector:
        """Get a detector by name. For now, we use the list detectors API directly.

        TODO: Properly model this in the API, and generate SDK code for it.
        """
        url = f"{self.configuration.host}/v1/detectors?name={name}"
        headers = self._headers()
        response = requests.request("GET", url, headers=headers, verify=self.configuration.verify_ssl)

        if not is_ok(response.status_code):
            raise InternalApiError(status=response.status_code, http_resp=response)

        parsed = response.json()

        if parsed["count"] == 0:
            raise NotFoundError(f"Detector with name={name} not found.")
        if parsed["count"] > 1:
            raise RuntimeError(
                f"We found multiple ({parsed['count']}) detectors with the same name. This shouldn't happen.",
            )
        return Detector.parse_obj(parsed["results"][0])

    @RequestsRetryDecorator()
    def start_inspection(self) -> str:
        """Starts an inspection, returns the ID."""
        url = f"{self.configuration.host}/inspections"

        headers = self._headers()

        response = requests.request("POST", url, headers=headers, json={}, verify=self.configuration.verify_ssl)

        if not is_ok(response.status_code):
            raise InternalApiError(
                status=response.status_code,
                reason="Error starting inspection.",
                http_resp=response,
            )

        return response.json()["id"]

    @RequestsRetryDecorator()
    def update_inspection_metadata(self, inspection_id: str, user_provided_key: str, user_provided_value: str) -> None:
        """Add/update inspection metadata with the user_provided_key and user_provided_value.

        The API stores inspections metadata in two ways:
           1) At the top level of the inspection with user_provided_id_key and user_provided_id_value. This is a
              kind of "primary" piece of metadata for the inspection. Only one key/value pair is allowed at this level.
           2) In the user_metadata field as a dictionary.  Multiple key/value pairs are allowed at this level.

        The first piece of metadata presented to an inspection will be assumed to be the user_provided_id_key and
        user_provided_id_value. All subsequent pieces metadata will be stored in the user_metadata field.

        """
        url = f"{self.configuration.host}/inspections/{inspection_id}"

        headers = self._headers()

        # Get inspection in order to find out:
        # 1) if user_provided_id_key has been set
        # 2) if the inspection is closed
        response = requests.request("GET", url, headers=headers, verify=self.configuration.verify_ssl)

        if not is_ok(response.status_code):
            raise InternalApiError(
                status=response.status_code,
                reason=f"Error getting inspection details for inspection {inspection_id}.",
                http_resp=response,
            )
        if response.json()["status"] == "COMPLETE":
            raise ValueError(f"Inspection {inspection_id} is closed. Metadata cannot be added.")

        payload = {}

        # Set the user_provided_id_key and user_provided_id_value if they were not previously set.
        response_json = response.json()
        if not response_json.get("user_provided_id_key"):
            payload["user_provided_id_key"] = user_provided_key
            payload["user_provided_id_value"] = user_provided_value

        # Get the existing keys and values in user_metadata (if any) so that we don't overwrite them.
        metadata = response_json["user_metadata"]
        if not metadata:
            metadata = {}

        # Submit the new metadata
        metadata[user_provided_key] = user_provided_value
        payload["user_metadata_json"] = json.dumps(metadata)
        response = requests.request("PATCH", url, headers=headers, json=payload, verify=self.configuration.verify_ssl)

        if not is_ok(response.status_code):
            raise InternalApiError(
                status=response.status_code,
                reason=f"Error updating inspection metadata on inspection {inspection_id}.",
                http_resp=response,
            )

    @RequestsRetryDecorator()
    def stop_inspection(self, inspection_id: str) -> str:
        """Stops an inspection and raises an exception if the response from the server does not indicate success.
        Returns a string that indicates the result (either PASS or FAIL). The URCap requires this.
        """
        url = f"{self.configuration.host}/inspections/{inspection_id}"

        headers = self._headers()

        # Closing an inspection generates a new inspection PDF. Therefore, if the inspection
        # is already closed, just return "COMPLETE" to avoid unnecessarily generating a new PDF.
        response = requests.request("GET", url, headers=headers, verify=self.configuration.verify_ssl)

        if not is_ok(response.status_code):
            raise InternalApiError(
                status=response.status_code,
                reason=f"Error checking the status of {inspection_id}.",
                http_resp=response,
            )

        if response.json().get("status") == "COMPLETE":
            return "COMPLETE"

        payload = {"status": "COMPLETE"}

        response = requests.request("PATCH", url, headers=headers, json=payload, verify=self.configuration.verify_ssl)

        if not is_ok(response.status_code):
            raise InternalApiError(
                status=response.status_code,
                reason=f"Error stopping inspection {inspection_id}.",
                http_resp=response,
            )

        return response.json()["result"]

    @RequestsRetryDecorator()
    def update_detector_confidence_threshold(self, detector_id: str, confidence_threshold: float) -> None:
        """Updates the confidence threshold of a detector."""

        # The API does not validate the confidence threshold,
        # so we will validate it here and raise an exception if necessary.
        if confidence_threshold < 0 or confidence_threshold > 1:
            raise ValueError(f"Confidence threshold must be between 0 and 1. Got {confidence_threshold}.")

        url = f"{self.configuration.host}/predictors/{detector_id}"

        headers = self._headers()

        payload = {"confidence_threshold": confidence_threshold}

        response = requests.request("PATCH", url, headers=headers, json=payload, verify=self.configuration.verify_ssl)

        if not is_ok(response.status_code):
            raise InternalApiError(
                status=response.status_code,
                reason=f"Error updating detector: {detector_id}.",
                http_resp=response,
            )
