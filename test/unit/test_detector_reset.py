import time
from datetime import datetime

import pytest
from groundlight import ExperimentalApi
from groundlight_openapi_client.exceptions import NotFoundException


def test_reset(gl_experimental: ExperimentalApi):
    # Reset the detector
    det = gl_experimental.create_detector(f"Test {datetime.utcnow()}", "test_query")
    iq = gl_experimental.submit_image_query(det, "test/assets/cat.jpeg")
    gl_experimental.reset_detector(det.id)
    time.sleep(900)
    with pytest.raises(NotFoundException):
        gl_experimental.get_image_query(iq.id)


def test_reset_training(gl_experimental: ExperimentalApi):
    # If we reset a detector, we should have low confidence after the reset
    LOW_CONFIDENCE_THRESHOLD = 0.6
    det = gl_experimental.get_or_create_detector("Test Detector for Resets", "is this a cat?")
    iq = gl_experimental.submit_image_query(det, "test/assets/cat.jpeg")
    assert iq.result.confidence < LOW_CONFIDENCE_THRESHOLD