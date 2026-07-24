import io
import logging
import os
import platform
import random
import time
import uuid
from enum import Enum
from functools import wraps
from http import HTTPStatus
from typing import Callable, Dict, Optional, Tuple, Union
from urllib.parse import urlsplit, urlunsplit

import requests
from groundlight_openapi_client.api_client import ApiClient, ApiException
from model import Detector, ImageQuery

from groundlight.status_codes import is_ok
from groundlight.version import get_version

logger = logging.getLogger("groundlight.sdk")
REQUEST_BODY_ARG_INDEX = 5


class NotFoundError(Exception):
    pass


def api_exception_detail(exc: ApiException) -> Optional[str]:
    """Return a stripped response body from an API exception, if present."""
    body = exc.body
    if body is None:
        return None
    if isinstance(body, bytes):
        text = body.decode("utf-8", errors="replace")
    else:
        text = str(body)
    text = text.strip()
    return text or None


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
            f"Invalid API endpoint {endpoint}.  Unsupported scheme: {parts.scheme}.  Must be http or https, e.g."
            " https://api.groundlight.ai/",
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
    The only subtlety here is that currently confidence of None means
    human label, which is treated as confident.
    """
    if not iq.result or not iq.result.confidence:
        return False
    return iq.result.confidence >= confidence_threshold  # type: ignore


def iq_is_answered(iq: ImageQuery) -> bool:
    """Returns True if the image query has a ML or human label.
    Placeholder and special labels (out of domain) have confidences exactly 0.5
    """
    if not iq.result or not iq.result.source:
        return False
    if (iq.result.source == "STILL_PROCESSING") or (iq.result.source is None):  # Should never be None
        return False
    return True


class InternalApiError(ApiException, RuntimeError):
    # TODO: We should really avoid this double inheritance since
    # both `ApiException` and `RuntimeError` are subclasses of
    # `Exception`. Error handling might become more complex since
    # the two super classes cross paths.
    # pylint: disable=useless-super-delegation
    def __init__(self, status=None, reason=None, http_resp=None):
        super().__init__(status, reason, http_resp)


class RequestsRetryDecorator:  # pylint: disable=too-few-public-methods
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
                                f"Current HTTP response status: {status_code}. "
                                f"Remaining retries: {self.max_retries - retry_count}. "
                                f"Delaying {random_delay:.1f}s before retrying.",
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
        """Initialize the generated API client with SDK-specific behavior."""
        super().__init__(*args, **kwargs)
        self.user_agent = f"Groundlight-Python-SDK/{get_version()}/{platform.platform()}/{platform.python_version()}"
        self._unauthorized_handler: Optional[Callable[[Optional[str]], None]] = None

    REQUEST_ID_HEADER = "X-Request-Id"

    def set_unauthorized_handler(self, handler: Callable[[Optional[str]], None]) -> None:
        """Set the callback used to recover and retry after a 401 response."""
        self._unauthorized_handler = handler

    @staticmethod
    def _prepare_replayable_request_body(args: tuple, kwargs: dict) -> Tuple[tuple, dict, Optional[bytes], bool]:
        """Copy a stream body so each request attempt receives a fresh stream."""
        body_is_keyword = "body" in kwargs
        body = (
            kwargs.get("body")
            if body_is_keyword
            else (args[REQUEST_BODY_ARG_INDEX] if len(args) > REQUEST_BODY_ARG_INDEX else None)
        )
        if not isinstance(body, io.IOBase):
            return args, kwargs, None, body_is_keyword
        try:
            body_bytes = body.read()
        finally:
            body.close()
        if body_is_keyword:
            kwargs = dict(kwargs)
            kwargs["body"] = io.BytesIO(body_bytes)
        else:
            replayable_args = list(args)
            replayable_args[REQUEST_BODY_ARG_INDEX] = io.BytesIO(body_bytes)
            args = tuple(replayable_args)
        return args, kwargs, body_bytes, body_is_keyword

    @RequestsRetryDecorator()
    def call_api(self, *args, **kwargs):
        """Add a request ID and retry once after token recovery from a 401."""
        args, kwargs, replayable_body, body_is_keyword = self._prepare_replayable_request_body(args, kwargs)
        # Note we don't look for header_param in kwargs here, because this method is only called in one place
        # in the generated code, so we can afford to make this brittle.
        header_param = args[4]  # that's the number in the list
        if header_param is None:
            # This will never happen in normal usage.
            logger.warning("Can't set request-id because headers not set")
        elif not header_param.get(self.REQUEST_ID_HEADER, None):
            header_param[self.REQUEST_ID_HEADER] = _generate_request_id()
            # Note that we have updated the actual dict in args, so we don't have to put it back in
        try:
            return super().call_api(*args, **kwargs)
        except ApiException as exc:
            if exc.status != HTTPStatus.UNAUTHORIZED or self._unauthorized_handler is None:
                raise
            self._unauthorized_handler(api_exception_detail(exc))
            retry_args = list(args)
            retry_kwargs = dict(kwargs)
            if replayable_body is not None:
                if body_is_keyword:
                    retry_kwargs["body"] = io.BytesIO(replayable_body)
                else:
                    retry_args[REQUEST_BODY_ARG_INDEX] = io.BytesIO(replayable_body)
            return super().call_api(*retry_args, **retry_kwargs)

    def request_with_unauthorized_recovery(self, method: str, url: str, **kwargs) -> requests.Response:
        """Send a raw request and retry once with refreshed credentials after a 401."""
        files_snapshot = self._snapshot_multipart_files(kwargs.get("files"))
        request_kwargs = dict(kwargs)
        if files_snapshot is not None:
            request_kwargs["files"] = self._files_from_snapshot(files_snapshot)

        response = requests.request(method, url, **request_kwargs)
        if response.status_code != HTTPStatus.UNAUTHORIZED or self._unauthorized_handler is None:
            return response
        detail = (response.text or "").strip() or None
        self._unauthorized_handler(detail)
        headers = dict(request_kwargs.get("headers", {}))
        headers["x-api-token"] = self.configuration.api_key["ApiToken"]
        request_kwargs["headers"] = headers
        if files_snapshot is not None:
            request_kwargs["files"] = self._files_from_snapshot(files_snapshot)
        return requests.request(method, url, **request_kwargs)

    @staticmethod
    def _read_multipart_file_bytes(fileobj) -> bytes:
        """Read bytes from a multipart file value without assuming it is seekable."""
        if isinstance(fileobj, (bytes, bytearray)):
            return bytes(fileobj)
        if isinstance(fileobj, io.IOBase):
            data = fileobj.read()
            if isinstance(data, str):
                return data.encode("utf-8")
            return data
        raise TypeError(f"Unsupported multipart file type: {type(fileobj)!r}")

    @classmethod
    def _snapshot_multipart_files(cls, files) -> Optional[Dict[str, Union[bytes, Tuple]]]:
        """Copy multipart file payloads so a 401 retry can resend them."""
        if files is None:
            return None
        snapshot: Dict[str, Union[bytes, Tuple]] = {}
        for field, value in files.items():
            if isinstance(value, tuple):
                filename, fileobj, *rest = value
                snapshot[field] = (filename, cls._read_multipart_file_bytes(fileobj), *rest)
            else:
                snapshot[field] = cls._read_multipart_file_bytes(value)
        return snapshot

    @staticmethod
    def _files_from_snapshot(snapshot: Dict[str, Union[bytes, Tuple]]) -> Dict[str, Union[io.BytesIO, Tuple]]:
        """Rebuild a requests-compatible files dict from a bytes snapshot."""
        files: Dict[str, Union[io.BytesIO, Tuple]] = {}
        for field, value in snapshot.items():
            if isinstance(value, tuple):
                filename, data, *rest = value
                files[field] = (filename, io.BytesIO(data), *rest)
            else:
                files[field] = io.BytesIO(value)
        return files

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
        logger.warning("This method is slated for removal, instead use the labels_api in the groundlight client")
        # TODO: Properly model this with OpenApi spec.
        start_time = time.time()
        url = f"{self.configuration.host}/labels"

        # TODO: remove posicheck_id
        data = {"label": label, "posicheck_id": image_query_id, "review_reason": ReviewReason.CUSTOMER_INITIATED}

        headers = self._headers()

        logger.info(f"Posting label={label} to image_query {image_query_id} ...")
        response = self.request_with_unauthorized_recovery(
            "POST", url, json=data, headers=headers, verify=self.configuration.verify_ssl
        )
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
        response = self.request_with_unauthorized_recovery(
            "GET", url, headers=headers, verify=self.configuration.verify_ssl
        )

        if not is_ok(response.status_code):
            raise InternalApiError(status=response.status_code, http_resp=response)

        parsed = response.json()

        if parsed["count"] == 0:
            raise NotFoundError(f"Detector with name={name} not found.")
        if parsed["count"] > 1:
            raise RuntimeError(
                f"We found multiple ({parsed['count']}) detectors with the same name. This shouldn't happen.",
            )
        return Detector.model_validate(parsed["results"][0])
