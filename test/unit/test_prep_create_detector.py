"""Unit tests for Groundlight._prep_create_detector.

These build the detector-creation request body without a live server, so they check exactly which
fields the SDK sends to the create-detector endpoint.
"""

from typing import Iterator
from unittest.mock import MagicMock, patch

import pytest
from groundlight import Groundlight

# Long enough for TokenManager's snippet validation (>= 20 chars).
_FAKE_API_TOKEN = "api_fake_test_token_xx"


@pytest.fixture(name="gl")
def offline_gl_fixture(monkeypatch) -> Iterator[Groundlight]:
    """Build a Groundlight client without live connectivity or token-rotation network calls."""
    monkeypatch.setenv("GROUNDLIGHT_API_TOKEN", _FAKE_API_TOKEN)
    with (
        patch("groundlight.client.TokenManager", return_value=MagicMock()),
        patch.object(Groundlight, "_verify_connectivity", return_value=None),
    ):
        yield Groundlight(endpoint="http://test-server/device-api/")


@pytest.mark.parametrize("confidence_threshold", [0.0, 0.75, 1.0])
def test_confidence_threshold_is_sent(gl: Groundlight, confidence_threshold: float):
    """A caller-supplied confidence_threshold is sent, including 0.0."""
    detector_creation_input = gl._prep_create_detector(  # pylint: disable=protected-access
        "test detector", "Is there a dog?", confidence_threshold=confidence_threshold
    )
    assert detector_creation_input.to_dict()["confidence_threshold"] == confidence_threshold


def test_confidence_threshold_omitted_when_none(gl: Groundlight):
    """With no confidence_threshold, the field is left out so the server applies its default."""
    detector_creation_input = gl._prep_create_detector(  # pylint: disable=protected-access
        "test detector", "Is there a dog?"
    )
    assert "confidence_threshold" not in detector_creation_input.to_dict()
