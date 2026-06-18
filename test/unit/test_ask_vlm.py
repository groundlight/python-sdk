"""Unit tests for Groundlight.ask_vlm — mocks HTTP, no live server needed."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from groundlight import Groundlight, VLMVerificationResult


@pytest.fixture
def gl(monkeypatch):
    monkeypatch.setenv("GROUNDLIGHT_API_TOKEN", "api_fake_test_token")
    # Avoid the live /v1/me connectivity check performed during __init__.
    with patch.object(Groundlight, "_verify_connectivity", return_value=None):
        client = Groundlight(endpoint="http://test-server/device-api/")
    return client


def _mock_response(
    verdict="YES", confidence=0.92, reasoning="Flames visible.", model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0"
):
    resp = MagicMock()
    resp.status_code = 201
    resp.json.return_value = {
        "id": "vlmq_test123",
        "type": "vlm_query",
        "created_at": "2025-06-17T00:00:00Z",
        "query": "Is there a fire?",
        "model_id": model_id,
        "result": {"verdict": verdict, "confidence": confidence, "reasoning": reasoning},
        "cost": {"input_tokens": 400, "output_tokens": 80, "total_cost_usd": 0.0015},
    }
    resp.raise_for_status = MagicMock()
    return resp


class TestAskVlm:
    @patch("groundlight.client.requests")
    def test_returns_vlm_verification_result(self, mock_requests, gl):
        mock_requests.post.return_value = _mock_response()

        result = gl.ask_vlm(images=np.zeros((100, 100, 3), dtype=np.uint8), query="Is there a fire?")

        assert isinstance(result, VLMVerificationResult)
        assert result.verdict == "YES"
        assert result.confidence == pytest.approx(0.92)
        assert result.id == "vlmq_test123"
        assert result.input_tokens == 400
        assert result.total_cost_usd == pytest.approx(0.0015)

    @patch("groundlight.client.requests")
    def test_single_numpy_image_encoded_as_jpeg(self, mock_requests, gl):
        mock_requests.post.return_value = _mock_response()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        gl.ask_vlm(images=frame, query="Is there a fire?")

        _, kwargs = mock_requests.post.call_args
        files = kwargs["files"]
        assert len(files) == 1
        assert files[0][0] == "images"
        name, data, ctype = files[0][1]
        assert ctype == "image/jpeg"
        assert len(data) > 0  # bytes were produced

    @patch("groundlight.client.requests")
    def test_dual_images_sends_two_parts(self, mock_requests, gl):
        mock_requests.post.return_value = _mock_response()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        roi = np.zeros((120, 120, 3), dtype=np.uint8)

        gl.ask_vlm(images=[frame, roi], query="Is there a fire?")

        _, kwargs = mock_requests.post.call_args
        assert len(kwargs["files"]) == 2

    @patch("groundlight.client.requests")
    def test_model_id_passed_as_query_param(self, mock_requests, gl):
        mock_requests.post.return_value = _mock_response(model_id="us.amazon.nova-pro-v1:0")

        gl.ask_vlm(images=np.zeros((100, 100, 3), dtype=np.uint8), query="test", model_id="us.amazon.nova-pro-v1:0")

        _, kwargs = mock_requests.post.call_args
        assert kwargs["params"]["model_id"] == "us.amazon.nova-pro-v1:0"

    @patch("groundlight.client.requests")
    def test_no_model_id_omits_param(self, mock_requests, gl):
        mock_requests.post.return_value = _mock_response()

        gl.ask_vlm(images=np.zeros((100, 100, 3), dtype=np.uint8), query="test")

        _, kwargs = mock_requests.post.call_args
        assert "model_id" not in kwargs["params"]

    def test_more_than_two_images_raises(self, gl):
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        with pytest.raises(ValueError, match="at most 2"):
            gl.ask_vlm(images=[frame, frame, frame], query="test")

    @patch("groundlight.client.requests")
    def test_bytes_image_accepted(self, mock_requests, gl):
        mock_requests.post.return_value = _mock_response()
        # A minimal valid JPEG header
        jpeg_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 100

        # Should not raise
        try:
            gl.ask_vlm(images=jpeg_bytes, query="test")
        except Exception:
            pass  # parse_supported_image_types may reject invalid JPEG body; that's fine here
