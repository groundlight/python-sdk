"""Unit tests for priming_group_id parameter in detector creation."""

from unittest import mock

import pytest
from groundlight import Groundlight
from model import Detector


@pytest.fixture(name="gl")
def groundlight_fixture() -> Groundlight:
    """Creates a Groundlight client."""
    return Groundlight()


@pytest.fixture(name="mock_detector_api")
def mock_detector_api_fixture():
    """Mock the detectors API."""
    with mock.patch("groundlight.client.DetectorsApi") as mock_api:
        # Setup a mock detector response
        mock_detector_response = mock.MagicMock()
        mock_detector_response.to_dict.return_value = {
            "id": "det_test123",
            "name": "test detector",
            "query": "Is there a dog?",
            "type": "binary",
            "created_at": "2024-01-01T00:00:00Z",
            "group_name": "default",
            "confidence_threshold": 0.9,
            "mode": "BINARY",
        }
        mock_api.return_value.create_detector.return_value = mock_detector_response
        yield mock_api


def test_create_detector_passes_priming_group_id(gl: Groundlight, mock_detector_api):
    """Test that priming_group_id is passed through to the API when creating a detector."""
    priming_group_id = "prgrp_test123456789012345678901234567890"

    detector = gl.create_detector(
        name="test detector",
        query="Is there a dog?",
        priming_group_id=priming_group_id,
    )

    # Verify the API was called
    assert mock_detector_api.return_value.create_detector.called

    # Get the detector_creation_input that was passed to the API
    call_args = mock_detector_api.return_value.create_detector.call_args
    detector_creation_input = call_args[0][0]

    # Verify priming_group_id was set correctly
    assert detector_creation_input.priming_group_id == priming_group_id
    assert isinstance(detector, Detector)


def test_create_binary_detector_passes_priming_group_id(gl: Groundlight, mock_detector_api):
    """Test that priming_group_id is passed through when creating a binary detector."""
    priming_group_id = "prgrp_test123456789012345678901234567890"

    detector = gl.create_binary_detector(
        name="test binary detector",
        query="Is there a cat?",
        priming_group_id=priming_group_id,
    )

    # Verify the API was called
    assert mock_detector_api.return_value.create_detector.called

    # Get the detector_creation_input that was passed to the API
    call_args = mock_detector_api.return_value.create_detector.call_args
    detector_creation_input = call_args[0][0]

    # Verify priming_group_id was set correctly
    assert detector_creation_input.priming_group_id == priming_group_id
    assert isinstance(detector, Detector)


def test_create_counting_detector_passes_priming_group_id(gl: Groundlight, mock_detector_api):
    """Test that priming_group_id is passed through when creating a counting detector."""
    priming_group_id = "prgrp_test123456789012345678901234567890"

    # Update mock response for counting detector
    mock_detector_response = mock.MagicMock()
    mock_detector_response.to_dict.return_value = {
        "id": "det_test456",
        "name": "test counting detector",
        "query": "How many dogs?",
        "type": "count",
        "created_at": "2024-01-01T00:00:00Z",
        "group_name": "default",
        "confidence_threshold": 0.9,
        "mode": "COUNT",
        "mode_configuration": {"class_name": "dog", "max_count": 10},
    }
    mock_detector_api.return_value.create_detector.return_value = mock_detector_response

    detector = gl.create_counting_detector(
        name="test counting detector",
        query="How many dogs?",
        class_name="dog",
        priming_group_id=priming_group_id,
    )

    # Verify the API was called
    assert mock_detector_api.return_value.create_detector.called

    # Get the detector_creation_input that was passed to the API
    call_args = mock_detector_api.return_value.create_detector.call_args
    detector_creation_input = call_args[0][0]

    # Verify priming_group_id was set correctly
    assert detector_creation_input.priming_group_id == priming_group_id
    assert isinstance(detector, Detector)


def test_create_multiclass_detector_passes_priming_group_id(gl: Groundlight, mock_detector_api):
    """Test that priming_group_id is passed through when creating a multiclass detector."""
    priming_group_id = "prgrp_test123456789012345678901234567890"

    # Update mock response for multiclass detector
    mock_detector_response = mock.MagicMock()
    mock_detector_response.to_dict.return_value = {
        "id": "det_test789",
        "name": "test multiclass detector",
        "query": "What animal?",
        "type": "multiclass",
        "created_at": "2024-01-01T00:00:00Z",
        "group_name": "default",
        "confidence_threshold": 0.9,
        "mode": "MULTI_CLASS",
        "mode_configuration": {"class_names": ["dog", "cat", "bird"]},
    }
    mock_detector_api.return_value.create_detector.return_value = mock_detector_response

    detector = gl.create_multiclass_detector(
        name="test multiclass detector",
        query="What animal?",
        class_names=["dog", "cat", "bird"],
        priming_group_id=priming_group_id,
    )

    # Verify the API was called
    assert mock_detector_api.return_value.create_detector.called

    # Get the detector_creation_input that was passed to the API
    call_args = mock_detector_api.return_value.create_detector.call_args
    detector_creation_input = call_args[0][0]

    # Verify priming_group_id was set correctly
    assert detector_creation_input.priming_group_id == priming_group_id
    assert isinstance(detector, Detector)


def test_create_detector_without_priming_group_id(gl: Groundlight, mock_detector_api):
    """Test that detector creation works without priming_group_id (backwards compatibility)."""
    detector = gl.create_detector(
        name="test detector no priming",
        query="Is there a dog?",
    )

    # Verify the API was called
    assert mock_detector_api.return_value.create_detector.called

    # Get the detector_creation_input that was passed to the API
    call_args = mock_detector_api.return_value.create_detector.call_args
    detector_creation_input = call_args[0][0]

    # Verify priming_group_id was not set (None or not present)
    assert not hasattr(detector_creation_input, "priming_group_id") or detector_creation_input.priming_group_id is None
    assert isinstance(detector, Detector)


def test_create_bounding_box_detector_passes_priming_group_id(mock_detector_api):
    """Test that priming_group_id is passed through when creating a bounding box detector."""
    from groundlight import ExperimentalApi

    gl_exp = ExperimentalApi()
    priming_group_id = "prgrp_test123456789012345678901234567890"

    # Update mock response for bounding box detector
    mock_detector_response = mock.MagicMock()
    mock_detector_response.to_dict.return_value = {
        "id": "det_testbbox",
        "name": "test bbox detector",
        "query": "Draw boxes around dogs",
        "type": "bounding_box",
        "created_at": "2024-01-01T00:00:00Z",
        "group_name": "default",
        "confidence_threshold": 0.9,
        "mode": "BOUNDING_BOX",
        "mode_configuration": {"class_name": "dog", "max_num_bboxes": 10},
    }
    mock_detector_api.return_value.create_detector.return_value = mock_detector_response

    detector = gl_exp.create_bounding_box_detector(
        name="test bbox detector",
        query="Draw boxes around dogs",
        class_name="dog",
        priming_group_id=priming_group_id,
    )

    # Verify the API was called
    assert mock_detector_api.return_value.create_detector.called

    # Get the detector_creation_input that was passed to the API
    call_args = mock_detector_api.return_value.create_detector.call_args
    detector_creation_input = call_args[0][0]

    # Verify priming_group_id was set correctly
    assert detector_creation_input.priming_group_id == priming_group_id
    assert isinstance(detector, Detector)


def test_create_text_recognition_detector_passes_priming_group_id(mock_detector_api):
    """Test that priming_group_id is passed through when creating a text recognition detector."""
    from groundlight import ExperimentalApi

    gl_exp = ExperimentalApi()
    priming_group_id = "prgrp_test123456789012345678901234567890"

    # Update mock response for text recognition detector
    mock_detector_response = mock.MagicMock()
    mock_detector_response.to_dict.return_value = {
        "id": "det_testtext",
        "name": "test text detector",
        "query": "Read the text",
        "type": "text",
        "created_at": "2024-01-01T00:00:00Z",
        "group_name": "default",
        "confidence_threshold": 0.9,
        "mode": "TEXT",
        "mode_configuration": {},
    }
    mock_detector_api.return_value.create_detector.return_value = mock_detector_response

    detector = gl_exp.create_text_recognition_detector(
        name="test text detector",
        query="Read the text",
        priming_group_id=priming_group_id,
    )

    # Verify the API was called
    assert mock_detector_api.return_value.create_detector.called

    # Get the detector_creation_input that was passed to the API
    call_args = mock_detector_api.return_value.create_detector.call_args
    detector_creation_input = call_args[0][0]

    # Verify priming_group_id was set correctly
    assert detector_creation_input.priming_group_id == priming_group_id
    assert isinstance(detector, Detector)
