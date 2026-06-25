"""Unit tests for Groundlight.ask_vlm — all HTTP mocked, no live server needed."""

from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
from groundlight import Groundlight, VLMVerificationResult
from groundlight.client import MAX_VLM_MEDIA_ITEMS
from groundlight.optional_imports import MISSING_NUMPY, np

# Minimal valid-looking JPEG bytes for tests that don't exercise image encoding.
_FAKE_JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 16


@pytest.fixture(name="gl")
def groundlight_fixture(monkeypatch) -> Groundlight:
    monkeypatch.setenv("GROUNDLIGHT_API_TOKEN", "api_fake_test_token")
    with patch.object(Groundlight, "_verify_connectivity", return_value=None):
        return Groundlight(endpoint="http://test-server/device-api/")


def _mock_response(verdict="YES", confidence=0.92, reasoning="Flames visible.", model_id="gpt-5.4"):
    resp = MagicMock()
    resp.status_code = 201
    resp.json.return_value = {
        "id": "vlmv_test123",
        "type": "vlm_verification",
        "created_at": "2025-06-17T00:00:00Z",
        "query": "Is there a fire?",
        "model_id": model_id,
        "result": {"verdict": verdict, "confidence": confidence, "reasoning": reasoning},
        "cost": {"input_tokens": 400, "output_tokens": 80, "total_cost_usd": 0.0015},
    }
    resp.raise_for_status = MagicMock()
    return resp


def test_returns_vlm_verification_result(gl: Groundlight):
    """Result fields are correctly unpacked from the server response JSON."""
    with mock.patch("groundlight.client.requests") as mock_requests:
        mock_requests.post.return_value = _mock_response()
        result = gl.ask_vlm(media=_FAKE_JPEG, query="Is there a fire?")

    assert isinstance(result, VLMVerificationResult)
    assert result.verdict == "YES"
    assert result.confidence == pytest.approx(0.92)
    assert result.id == "vlmv_test123"
    assert result.total_cost_usd == pytest.approx(0.0015)


@pytest.mark.skipif(MISSING_NUMPY, reason="Needs numpy")
def test_numpy_image_encoded_as_jpeg_multipart(gl: Groundlight):
    """A numpy array is converted to JPEG and sent as a multipart 'media' part."""
    with mock.patch("groundlight.client.requests") as mock_requests:
        mock_requests.post.return_value = _mock_response()
        gl.ask_vlm(media=np.zeros((480, 640, 3), dtype=np.uint8), query="Is there a fire?")

    _, kwargs = mock_requests.post.call_args
    files = kwargs["files"]
    assert len(files) == 1
    assert files[0][0] == "media"
    _name, data, ctype = files[0][1]
    assert ctype == "image/jpeg"
    assert len(data) > 0


def test_query_sent_as_form_field_not_url_param(gl: Groundlight):
    """query and model_id go in the multipart body — never the URL — so the prompt
    doesn't leak into access logs."""
    with mock.patch("groundlight.client.requests") as mock_requests:
        mock_requests.post.return_value = _mock_response(model_id="nova-pro")
        gl.ask_vlm(media=_FAKE_JPEG, query="Is there a fire?", model_id="nova-pro")

    _, kwargs = mock_requests.post.call_args
    assert kwargs["data"]["query"] == "Is there a fire?"
    assert kwargs["data"]["model_id"] == "nova-pro"
    assert "params" not in kwargs or not kwargs.get("params")


def test_more_than_max_media_raises(gl: Groundlight):
    """Supplying more than MAX_VLM_MEDIA_ITEMS raises ValueError before any network call."""
    with pytest.raises(ValueError, match=f"at most {MAX_VLM_MEDIA_ITEMS}"):
        gl.ask_vlm(media=[_FAKE_JPEG] * (MAX_VLM_MEDIA_ITEMS + 1), query="test")


def test_url_has_correct_path(gl: Groundlight):
    """sanitize_endpoint_url strips the trailing slash from self.endpoint, so the path
    must include a leading '/' — without it the URL becomes '...device-apiv1/...'."""
    with mock.patch("groundlight.client.requests") as mock_requests:
        mock_requests.post.return_value = _mock_response()
        gl.ask_vlm(media=_FAKE_JPEG, query="test")

    args, _ = mock_requests.post.call_args
    assert "/device-api/v1/vlm-verifications" in args[0]


def test_url_no_version_duplication_for_versioned_endpoint(monkeypatch):
    """When the endpoint already ends with /v1 the URL must not contain /v1/v1/."""
    monkeypatch.setenv("GROUNDLIGHT_API_TOKEN", "api_fake_test_token")
    with patch.object(Groundlight, "_verify_connectivity", return_value=None):
        gl_v1 = Groundlight(endpoint="http://test-server/v1")
    with mock.patch("groundlight.client.requests") as mock_requests:
        mock_requests.post.return_value = _mock_response()
        gl_v1.ask_vlm(media=_FAKE_JPEG, query="test")
    args, _ = mock_requests.post.call_args
    url = args[0]
    assert "/v1/v1/" not in url
    assert url.endswith("/v1/vlm-verifications")
