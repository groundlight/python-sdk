"""Unit tests for Groundlight.ask_vlm — all HTTP mocked, no live server needed."""

from unittest import mock
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from groundlight import Groundlight, VLMVerificationResult


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
    """ask_vlm returns a typed VLMVerificationResult with all expected fields populated."""
    with mock.patch("groundlight.client.requests") as mock_requests:
        mock_requests.post.return_value = _mock_response()
        result = gl.ask_vlm(media=np.zeros((100, 100, 3), dtype=np.uint8), query="Is there a fire?")

    assert isinstance(result, VLMVerificationResult)
    assert result.verdict == "YES"
    assert result.confidence == pytest.approx(0.92)
    assert result.id == "vlmv_test123"
    assert result.input_tokens == 400
    assert result.total_cost_usd == pytest.approx(0.0015)


def test_single_numpy_image_encoded_as_jpeg(gl: Groundlight):
    """A numpy array is encoded to JPEG and sent as a single multipart 'media' part."""
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


def test_dual_images_sends_two_parts(gl: Groundlight):
    """Passing a list of two images sends two 'media' multipart parts."""
    with mock.patch("groundlight.client.requests") as mock_requests:
        mock_requests.post.return_value = _mock_response()
        gl.ask_vlm(
            media=[np.zeros((480, 640, 3), dtype=np.uint8), np.zeros((120, 120, 3), dtype=np.uint8)],
            query="Is there a fire?",
        )

    _, kwargs = mock_requests.post.call_args
    assert len(kwargs["files"]) == 2


def test_url_has_correct_path(gl: Groundlight):
    """sanitize_endpoint_url strips the trailing slash, so we must insert '/' before
    the path — without it the URL would be '...device-apiv1/vlm-verifications'."""
    with mock.patch("groundlight.client.requests") as mock_requests:
        mock_requests.post.return_value = _mock_response()
        gl.ask_vlm(media=np.zeros((100, 100, 3), dtype=np.uint8), query="test")

    args, _ = mock_requests.post.call_args
    url = args[0]
    assert "/device-api/v1/vlm-verifications" in url


def test_query_and_model_id_sent_as_form_fields(gl: Groundlight):
    """query and model_id go in the multipart body, never in the URL query string."""
    with mock.patch("groundlight.client.requests") as mock_requests:
        mock_requests.post.return_value = _mock_response(model_id="nova-pro")
        gl.ask_vlm(media=np.zeros((100, 100, 3), dtype=np.uint8), query="Is there a fire?", model_id="nova-pro")

    _, kwargs = mock_requests.post.call_args
    assert kwargs["data"]["query"] == "Is there a fire?"
    assert kwargs["data"]["model_id"] == "nova-pro"
    assert "params" not in kwargs or not kwargs.get("params")


def test_no_model_id_omits_field(gl: Groundlight):
    """Omitting model_id leaves the field out entirely so the server uses its default."""
    with mock.patch("groundlight.client.requests") as mock_requests:
        mock_requests.post.return_value = _mock_response()
        gl.ask_vlm(media=np.zeros((100, 100, 3), dtype=np.uint8), query="test")

    _, kwargs = mock_requests.post.call_args
    assert "model_id" not in kwargs["data"]


def test_more_than_eight_media_raises(gl: Groundlight):
    """Supplying more than 8 media items raises ValueError before any network call."""
    with pytest.raises(ValueError, match="at most 8"):
        gl.ask_vlm(media=[np.zeros((100, 100, 3), dtype=np.uint8)] * 9, query="test")


def test_timeout_passed_to_requests(gl: Groundlight):
    """The timeout parameter is forwarded to requests.post."""
    with mock.patch("groundlight.client.requests") as mock_requests:
        mock_requests.post.return_value = _mock_response()
        gl.ask_vlm(media=np.zeros((100, 100, 3), dtype=np.uint8), query="test", timeout=5.0)

    _, kwargs = mock_requests.post.call_args
    assert kwargs["timeout"] == pytest.approx(5.0)


def test_corrupted_image_bytes_raises_http_error(gl: Groundlight):
    """Corrupted bytes are not validated client-side — the server rejects them with a
    400, which raise_for_status() converts to requests.HTTPError."""
    error_resp = MagicMock()
    error_resp.status_code = 400
    error_resp.raise_for_status.side_effect = Exception("400 Bad Request")

    with mock.patch("groundlight.client.requests") as mock_requests:
        mock_requests.post.return_value = error_resp
        with pytest.raises(Exception, match="400"):
            gl.ask_vlm(media=b"this-is-not-a-valid-image", query="test")
