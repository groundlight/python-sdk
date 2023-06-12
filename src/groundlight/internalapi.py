import logging
import os
import random
import time
import uuid
from functools import wraps
from typing import Callable, Optional, TypeVar
from urllib.parse import urlsplit, urlunsplit

import requests
from model import Detector
from openapi_client.api_client import ApiClient
from typing_extensions import ParamSpec

from groundlight.status_codes import is_ok

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
    # TODO: use a ksuid instead of a uuid.  Most of our API uses ksuids for lots of reasons.
    # But we don't want to just import ksuid because we want to avoid dependency bloat
    return "req_uu" + uuid.uuid4().hex


class InternalApiError(RuntimeError):
    # TODO: We need a better exception hierarchy
    def __init__(self, *args: object, status=None, reason=None, http_resp=None) -> None:
        super().__init__(*args)

        if http_resp:
            self.status = http_resp.status_code
            self.reason = http_resp.text
        else:
            self.status = status
            self.reason = reason

    def __str__(self):
        error_message = f"{self.status}\n Reason: {self.reason}"
        return error_message


ReturnType = TypeVar("ReturnType")
ParamsType = ParamSpec("ParamsType")


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

    def __call__(self, function: Callable[ParamsType, ReturnType]) -> Callable[ParamsType, ReturnType]:
        """:param callable: The function to invoke."""

        @wraps(function)
        def decorated(*args, **kwargs):
            delay = self.initial_delay
            retry_count = 0

            while retry_count <= self.max_retries:
                try:
                    return function(*args, **kwargs)
                except Exception as e:
                    # Properly model the exception hierarchy so that we don't catch
                    # too general an exception
                    is_http_error = hasattr(e, "status")
                    if not is_http_error:
                        raise e
                    if retry_count == self.max_retries:
                        raise InternalApiError(reason="Maximum retries reached") from e

                    if is_http_error:
                        status_code = e.status
                        if status_code in self.status_code_range:
                            logger.warning(
                                (
                                    f"Current HTTP response status: {status_code}. "
                                    f"Remaining retries: {self.max_retries - retry_count}"
                                ),
                                exc_info=True,
                            )
                            # This is implementing a full jitter strategy
                            random_delay = random.uniform(0, delay)
                            time.sleep(random_delay)

                retry_count += 1
                delay *= self.exponential_backoff

        return decorated


class GroundlightApiClient(ApiClient):
    """Subclassing the OpenAPI-generated ApiClient to add a bit of custom functionality.
    Not crazy about using polymorphism, but this is simpler than modifying the moustache
    templates in the generator to add the functionality.
    """

    REQUEST_ID_HEADER = "X-Request-Id"

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
        }

    @RequestsRetryDecorator()
    def _add_label(self, image_query_id: str, label: str) -> dict:
        """Temporary internal call to add a label to an image query.  Not supported."""
        # TODO: Properly model this with OpenApi spec.
        start_time = time.time()
        url = f"{self.configuration.host}/labels"

        data = {
            "label": label,
            "posicheck_id": image_query_id,
        }

        headers = self._headers()

        logger.info(f"Posting label={label} to image_query {image_query_id} ...")
        response = requests.request("POST", url, json=data, headers=headers)
        elapsed = 1000 * (time.time() - start_time)
        logger.debug(f"Call to ImageQuery.add_label took {elapsed:.1f}ms response={response.text}")

        if not is_ok(response.status_code):
            raise InternalApiError(reason=f"Error adding label to image query {image_query_id}", http_resp=response)

        return response.json()

    @RequestsRetryDecorator()
    def _get_detector_by_name(self, name: str) -> Detector:
        """Get a detector by name. For now, we use the list detectors API directly.

        TODO: Properly model this in the API, and generate SDK code for it.
        """
        url = f"{self.configuration.host}/v1/detectors?name={name}"
        headers = self._headers()
        response = requests.request("GET", url, headers=headers)

        if not is_ok(response.status_code):
            raise InternalApiError(http_resp=response)

        parsed = response.json()

        if parsed["count"] == 0:
            raise NotFoundError(f"Detector with name={name} not found.")
        if parsed["count"] > 1:
            raise RuntimeError(
                f"We found multiple ({parsed['count']}) detectors with the same name. This shouldn't happen.",
            )
        return Detector.parse_obj(parsed["results"][0])
