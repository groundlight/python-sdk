"""Unit tests for ExperimentalApi.generate_synthetic_image.

These mock the generated client's HTTP transport (RESTClientObject.request) so they exercise
the real request assembly (raw body, Content-Type, query params, auth) and response parsing
without a live server.
"""

import base64
import json
from typing import Iterator
from unittest.mock import MagicMock, patch

import groundlight
import pytest
from groundlight import ExperimentalApi
from groundlight.optional_imports import MISSING_NUMPY, np
from groundlight.synthetic_images import (
    DEFAULT_SYNTHETIC_IMAGE_CONNECT_TIMEOUT,
    DEFAULT_SYNTHETIC_IMAGE_READ_TIMEOUT,
    SyntheticImageResult,
)
from groundlight_openapi_client.rest import RESTClientObject
from model import SyntheticImage
from pydantic import ValidationError

# Minimal valid-looking image bytes. The transport is mocked, so these are never decoded.
_FAKE_JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 16
_FAKE_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
# Long enough for TokenManager's snippet validation (>= 20 chars).
_FAKE_API_TOKEN = "api_fake_test_token_xx"

# The image the server "generates", as it would come back: base64 in JSON.
_GENERATED_PNG = b"\x89PNG\r\n\x1a\n" + bytes(range(32))

_RESPONSE_JSON = json.dumps({
    "id": "synth_test123",
    "image": base64.b64encode(_GENERATED_PNG).decode("ascii"),
    "width": 640,
    "height": 480,
    "label": "YES",
    "rois": [{
        "label": "person",
        "score": 0.91,
        "geometry": {
            "left": 0.1,
            "top": 0.2,
            "right": 0.3,
            "bottom": 0.4,
            "x": 0.2,
            "y": 0.3,
        },
    }],
    "added_roi_index": 0,
    "metadata": {"lens": "fence_climbing"},
}).encode()


@pytest.fixture(name="gl")
def experimental_fixture(monkeypatch) -> Iterator[ExperimentalApi]:
    """Build an ExperimentalApi without live connectivity or token-rotation network calls."""
    monkeypatch.setenv("GROUNDLIGHT_API_TOKEN", _FAKE_API_TOKEN)
    with (
        patch("groundlight.client.TokenManager", return_value=MagicMock()),
        patch.object(ExperimentalApi, "_verify_connectivity", return_value=None),
    ):
        yield ExperimentalApi(endpoint="http://test-server/device-api/")


def _capturing_transport(captured: dict, data: bytes = _RESPONSE_JSON):
    """Return a fake RESTClientObject.request that records its args.

    The image is sent as the whole body, and the query string is assembled inside the method
    being patched, so `body` and `query_params` are captured rather than the URL query.
    """

    def fake_request(self, method, url, **kwargs):  # noqa: ANN001
        captured["method"] = method
        captured["url"] = url
        captured["body"] = kwargs.get("body")
        captured["query_params"] = kwargs.get("query_params")
        captured["headers"] = kwargs.get("headers")
        captured["_request_timeout"] = kwargs.get("_request_timeout")
        resp = MagicMock()
        resp.status = 200
        resp.data = data
        resp.getheader = lambda name, default=None: ("application/json" if name.lower() == "content-type" else default)
        resp.getheaders = lambda: {"Content-Type": "application/json"}
        return resp

    return fake_request


def test_returns_decoded_png_bytes(gl: ExperimentalApi):
    """The base64 image is decoded to real PNG bytes, and annotations are parsed."""
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _capturing_transport(captured)):
        result = gl.generate_synthetic_image(_FAKE_JPEG, lens_type="fence_climbing")

    assert isinstance(result, SyntheticImageResult)
    # Exact equality distinguishes a real decode from pydantic coercing the base64
    # string into ASCII bytes.
    assert result.image == _GENERATED_PNG
    assert result.image.startswith(b"\x89PNG")
    assert (result.width, result.height) == (640, 480)
    assert result.label == "YES"
    assert result.added_roi_index == 0
    assert result.rois[0].label == "person"
    assert result.rois[0].geometry.left == pytest.approx(0.1)
    assert result.metadata == {"lens": "fence_climbing"}
    assert captured["method"] == "POST"
    assert captured["url"].endswith("/device-api/v1/synthetic-images")


def test_sends_raw_jpeg_body_with_jpeg_content_type(gl: ExperimentalApi):
    """The image is the entire request body, not multipart or JSON."""
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _capturing_transport(captured)):
        gl.generate_synthetic_image(_FAKE_JPEG, lens_type="fence_climbing")

    assert captured["body"] == _FAKE_JPEG
    assert captured["headers"]["Content-Type"] == "image/jpeg"


def test_png_input_keeps_png_content_type(gl: ExperimentalApi):
    """Regression test: PNG bytes must not be declared as image/jpeg.

    The generated client defaults to the first content type it knows about when none is
    given, so dropping the explicit _content_type would mislabel PNG bytes.
    """
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _capturing_transport(captured)):
        gl.generate_synthetic_image(_FAKE_PNG, lens_type="fence_climbing")

    assert captured["body"] == _FAKE_PNG
    assert captured["headers"]["Content-Type"] == "image/png"


@pytest.mark.skipif(MISSING_NUMPY, reason="Needs numpy")
def test_numpy_input_is_encoded_as_jpeg(gl: ExperimentalApi):
    """numpy arrays are JPEG-encoded before sending, so the declared type follows."""
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _capturing_transport(captured)):
        gl.generate_synthetic_image(np.zeros((48, 64, 3), dtype=np.uint8), lens_type="fence_climbing")

    assert captured["headers"]["Content-Type"] == "image/jpeg"
    assert captured["body"].startswith(b"\xff\xd8")


def test_lens_type_goes_in_query_string(gl: ExperimentalApi):
    """lens_type is a required query param; lens_config is omitted when unset."""
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _capturing_transport(captured)):
        gl.generate_synthetic_image(_FAKE_JPEG, lens_type="fence_climbing")

    params = dict(captured["query_params"])
    assert params["lens_type"] == "fence_climbing"
    assert "lens_config" not in params


def test_lens_config_dict_is_encoded_as_base64_json(gl: ExperimentalApi):
    """A dict is serialized deterministically and base64 url-safe encoded."""
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _capturing_transport(captured)):
        gl.generate_synthetic_image(_FAKE_JPEG, lens_type="fence_climbing", lens_config={"b": 2, "a": 1})

    encoded = dict(captured["query_params"])["lens_config"]
    assert json.loads(base64.urlsafe_b64decode(encoded)) == {"a": 1, "b": 2}


def test_lens_config_accepts_json_string(gl: ExperimentalApi):
    """A JSON string (the CLI path) encodes to the same value as the equivalent dict."""
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _capturing_transport(captured)):
        gl.generate_synthetic_image(_FAKE_JPEG, lens_type="fence_climbing", lens_config='{"b": 2, "a": 1}')

    encoded = dict(captured["query_params"])["lens_config"]
    assert json.loads(base64.urlsafe_b64decode(encoded)) == {"a": 1, "b": 2}


@pytest.mark.parametrize("bad_config", ["{not valid json", "plain text", "[1, 2, 3]"])
def test_invalid_lens_config_raises_without_request(gl: ExperimentalApi, bad_config: str):
    """Anything that is not a JSON object fails locally rather than after a round trip."""
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _capturing_transport(captured)):
        with pytest.raises(TypeError):
            gl.generate_synthetic_image(_FAKE_JPEG, lens_type="fence_climbing", lens_config=bad_config)

    assert not captured


def test_oversized_lens_config_raises_without_request(gl: ExperimentalApi):
    """Oversized configs are rejected locally, matching the server's 1KiB limit."""
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _capturing_transport(captured)):
        with pytest.raises(ValueError, match="too large"):
            gl.generate_synthetic_image(
                _FAKE_JPEG,
                lens_type="fence_climbing",
                lens_config={"padding": "x" * 1024},
            )

    assert not captured


def test_unrecognized_image_bytes_raise_without_request(gl: ExperimentalApi):
    """Only JPEG and PNG can be declared, so anything else fails locally."""
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _capturing_transport(captured)):
        with pytest.raises(ValueError, match="Only JPEG and PNG"):
            gl.generate_synthetic_image(b"GIF89a" + b"\x00" * 16, lens_type="fence_climbing")

    assert not captured


def test_empty_image_raises_without_request(gl: ExperimentalApi):
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _capturing_transport(captured)):
        with pytest.raises(ValueError, match="non-empty image"):
            gl.generate_synthetic_image(b"", lens_type="fence_climbing")

    assert not captured


def test_result_serializes_to_json(gl: ExperimentalApi):
    """Regression test for the CLI, which renders results via model_dump_json().

    Raw bytes are not JSON-serializable, so the model re-encodes them as base64 for JSON
    while keeping bytes for normal attribute access and model_dump().
    """
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _capturing_transport(captured)):
        result = gl.generate_synthetic_image(_FAKE_JPEG, lens_type="fence_climbing")

    dumped = json.loads(result.model_dump_json())
    assert base64.b64decode(dumped["image"]) == _GENERATED_PNG
    assert isinstance(result.model_dump()["image"], bytes)


def test_generated_model_still_declares_image_as_str():
    """Guard against spec drift.

    SyntheticImageResult exists only to turn the wire model's base64 string into bytes. If a
    regenerated spec changes that field, this fails so the override gets revisited.
    """
    # dict() rather than subscripting model_fields directly, which pylint cannot infer.
    assert dict(SyntheticImage.model_fields)["image"].annotation is str
    assert dict(SyntheticImageResult.model_fields)["image"].annotation is bytes


def test_sends_connect_and_read_timeout(gl: ExperimentalApi):
    """The timeout is a (connect, read) pair, not a scalar.

    A scalar becomes a total budget, which would charge uploading the source image against the
    time allowed for generation. Dropping the timeout entirely fails open -- urllib3 would wait
    forever -- so this asserts the value actually reaches the transport.
    """
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _capturing_transport(captured)):
        gl.generate_synthetic_image(_FAKE_JPEG, lens_type="fence_climbing")

    assert captured["_request_timeout"] == (
        DEFAULT_SYNTHETIC_IMAGE_CONNECT_TIMEOUT,
        DEFAULT_SYNTHETIC_IMAGE_READ_TIMEOUT,
    )


def test_timeout_override_changes_only_the_read_budget(gl: ExperimentalApi):
    """An explicit timeout extends the wait for generation, leaving the connect budget alone."""
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _capturing_transport(captured)):
        gl.generate_synthetic_image(_FAKE_JPEG, lens_type="fence_climbing", timeout=300.0)

    assert captured["_request_timeout"] == (DEFAULT_SYNTHETIC_IMAGE_CONNECT_TIMEOUT, 300.0)


def test_model_decodes_base64_without_caller_help():
    """The decode lives in the type, so it cannot be skipped by a new call site.

    pydantic's lax mode would otherwise accept the base64 string and ASCII-encode it, storing
    the text as the image and raising nothing.
    """
    payload = {
        "id": "s1",
        "image": base64.b64encode(_GENERATED_PNG).decode("ascii"),
        "width": 4,
        "height": 4,
        "label": "YES",
        "rois": [],
        "added_roi_index": 0,
        "metadata": {},
    }
    assert SyntheticImageResult.model_validate(payload).image == _GENERATED_PNG
    # Already-decoded bytes must pass through rather than being decoded twice.
    assert SyntheticImageResult.model_validate({**payload, "image": _GENERATED_PNG}).image == _GENERATED_PNG


@pytest.mark.parametrize(
    "bad_image",
    [
        pytest.param("", id="empty-string"),
        pytest.param(b"", id="empty-bytes"),
        pytest.param("!!!not base64!!!", id="not-base64"),
        pytest.param(base64.b64encode(b"x").decode("ascii")[:-1], id="bad-padding"),
    ],
)
def test_model_rejects_unusable_image(bad_image):
    """An empty or undecodable image is rejected, naming the field.

    Without this the caller would write a zero-byte or corrupt PNG to disk, and a malformed
    payload would surface as a bare binascii.Error with no mention of what failed.
    """
    payload = {
        "id": "s1",
        "image": bad_image,
        "width": 4,
        "height": 4,
        "label": "YES",
        "rois": [],
        "added_roi_index": 0,
        "metadata": {},
    }
    with pytest.raises(ValidationError, match="image"):
        SyntheticImageResult.model_validate(payload)


def test_empty_image_from_server_is_rejected(gl: ExperimentalApi):
    """End-to-end: a 200 carrying an empty image fails instead of yielding a 0-byte PNG."""
    body = json.dumps({
        "id": "s1",
        "image": "",
        "width": 4,
        "height": 4,
        "label": "YES",
        "rois": [],
        "added_roi_index": 0,
        "metadata": {},
    }).encode()
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _capturing_transport(captured, data=body)):
        with pytest.raises(ValidationError, match="image"):
            gl.generate_synthetic_image(_FAKE_JPEG, lens_type="fence_climbing")


def test_result_type_is_exported_from_the_package():
    """The return type must be reachable as `groundlight.SyntheticImageResult`.

    `from model import *` exports the wire model `SyntheticImage`, whose `image` is a base64
    str. Without this export someone annotating the return type reaches for that name and gets
    a type that disagrees with what is actually returned.
    """
    assert groundlight.SyntheticImageResult is SyntheticImageResult
    # dict() rather than subscripting model_fields directly, which pylint cannot infer.
    assert dict(groundlight.SyntheticImageResult.model_fields)["image"].annotation is bytes
    # The wire model stays reachable and unshadowed, for anyone who wants the base64 shape.
    assert dict(groundlight.SyntheticImage.model_fields)["image"].annotation is str
