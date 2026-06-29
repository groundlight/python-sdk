"""Unit tests for ExperimentalApi.ask_vlm_verify.

These mock the generated client's HTTP transport (RESTClientObject.request) so they exercise
the real request assembly (multipart parts, URL, auth) and response parsing without a live
server — the same layer the rest of the SDK's request plumbing runs through.
"""

from unittest.mock import MagicMock, patch

import pytest
from groundlight import ExperimentalApi
from groundlight.experimental_api import MAX_VLM_MEDIA_ITEMS
from groundlight.optional_imports import MISSING_NUMPY, np
from groundlight_openapi_client.rest import RESTClientObject
from model import VlmVerification

# Minimal valid-looking JPEG bytes for tests that don't exercise image encoding.
_FAKE_JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 16

_RESPONSE_JSON = (
    b'{"id":"vlmv_test123","type":"vlm_verification","created_at":"2025-06-17T00:00:00Z",'
    b'"query":"Is there a fire?","model_id":"gpt-5.4",'
    b'"result":{"verdict":"YES","confidence":0.92,"reasoning":"Flames visible."},'
    b'"cost":{"input_tokens":400,"output_tokens":80,"total_cost_usd":0.0015}}'
)


@pytest.fixture(name="gl")
def experimental_fixture(monkeypatch) -> ExperimentalApi:
    monkeypatch.setenv("GROUNDLIGHT_API_TOKEN", "api_fake_test_token")
    with patch.object(ExperimentalApi, "_verify_connectivity", return_value=None):
        return ExperimentalApi(endpoint="http://test-server/device-api/")


def _capturing_transport(captured: dict, data: bytes = _RESPONSE_JSON):
    """Return a fake RESTClientObject.request that records its args and returns a 201."""

    def fake_request(self, method, url, **kwargs):  # noqa: ANN001
        captured["method"] = method
        captured["url"] = url
        captured["post_params"] = kwargs.get("post_params")
        captured["headers"] = kwargs.get("headers")
        resp = MagicMock()
        resp.status = 201
        resp.data = data
        resp.getheader = lambda name, default=None: (
            "application/json" if name.lower() == "content-type" else default
        )
        resp.getheaders = lambda: {"Content-Type": "application/json"}
        return resp

    return fake_request


def test_returns_vlm_verification(gl: ExperimentalApi):
    """Server JSON is parsed into the generated VlmVerification model (nested result/cost)."""
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _capturing_transport(captured)):
        result = gl.ask_vlm_verify(media=_FAKE_JPEG, query="Is there a fire?")

    assert isinstance(result, VlmVerification)
    assert result.id == "vlmv_test123"
    assert result.result.verdict == "YES"
    assert result.result.confidence == pytest.approx(0.92)
    assert result.result.reasoning == "Flames visible."
    assert result.cost.total_cost_usd == pytest.approx(0.0015)
    assert result.cost.input_tokens is not None
    # Sanity: it went through the generated client to the right endpoint.
    assert captured["method"] == "POST"
    assert captured["url"].endswith("/device-api/v1/vlm-verifications")


@pytest.mark.skipif(MISSING_NUMPY, reason="Needs numpy")
def test_numpy_image_encoded_as_jpeg_multipart(gl: ExperimentalApi):
    """A numpy array is converted to JPEG and sent as a multipart 'media' part."""
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _capturing_transport(captured)):
        gl.ask_vlm_verify(media=np.zeros((480, 640, 3), dtype=np.uint8), query="Is there a fire?")

    media_parts = [p for p in captured["post_params"] if p[0] == "media"]
    assert len(media_parts) == 1
    filename, data, ctype = media_parts[0][1]
    assert ctype == "image/jpeg"
    assert len(data) > 0


def test_query_and_model_id_sent_as_form_fields(gl: ExperimentalApi):
    """query and model_id go in the multipart body, not the URL, so the prompt can't leak into logs."""
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _capturing_transport(captured)):
        gl.ask_vlm_verify(media=_FAKE_JPEG, query="Is there a fire?", model_id="nova-pro")

    fields = {p[0]: p[1] for p in captured["post_params"]}
    assert fields["query"] == "Is there a fire?"
    assert fields["model_id"] == "nova-pro"
    assert "query" not in captured["url"]
    assert "nova-pro" not in captured["url"]


def test_multiple_images_sent_as_separate_media_parts(gl: ExperimentalApi):
    """A list of images produces one 'media' part each."""
    num_images = 3
    captured: dict = {}
    with patch.object(RESTClientObject, "request", _capturing_transport(captured)):
        gl.ask_vlm_verify(media=[_FAKE_JPEG] * num_images, query="test")

    media_parts = [p for p in captured["post_params"] if p[0] == "media"]
    assert len(media_parts) == num_images


def test_empty_media_raises(gl: ExperimentalApi):
    """An empty media list raises ValueError before any network call."""
    with pytest.raises(ValueError, match="at least one media item"):
        gl.ask_vlm_verify(media=[], query="test")


def test_more_than_max_media_raises(gl: ExperimentalApi):
    """Supplying more than MAX_VLM_MEDIA_ITEMS raises ValueError before any network call."""
    with pytest.raises(ValueError, match=f"at most {MAX_VLM_MEDIA_ITEMS}"):
        gl.ask_vlm_verify(media=[_FAKE_JPEG] * (MAX_VLM_MEDIA_ITEMS + 1), query="test")
