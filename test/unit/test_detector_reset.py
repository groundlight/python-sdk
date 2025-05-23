import time
from datetime import datetime

import pytest
from groundlight import ExperimentalApi
from groundlight_openapi_client.exceptions import NotFoundException


@pytest.mark.skip(reason="This is an expensive test, reset may take some time")
def test_reset_retry(gl_experimental: ExperimentalApi):
    # Reset the detector, retrying in case the reset is still ongoing
    det = gl_experimental.create_detector(f"Test {datetime.utcnow()}", "test_query")
    iq = gl_experimental.submit_image_query(det, "test/assets/cat.jpeg")
    gl_experimental.reset_detector(det.id)
    success = False
    for _ in range(60):
        try:
            gl_experimental.get_image_query(iq.id)
        except NotFoundException:
            with pytest.raises(NotFoundException):
                gl_experimental.get_image_query(iq.id)
            success = True
            break
        time.sleep(10)
    if not success:
        raise Exception("Failed to reset detector")


@pytest.mark.skip(reason="This test does not work with strong 0 shot models, enabled by default based on your account")
def test_reset_training(gl_experimental: ExperimentalApi):
    # If we reset a detector, we should have low confidence after the reset
    low_confidence_threshold = 0.6
    det = gl_experimental.create_detector(f"Test {datetime.utcnow()}", "is this a cat")
    gl_experimental.reset_detector(det.id)
    iq = gl_experimental.submit_image_query(det, "test/assets/cat.jpeg", human_review="NEVER")
    assert iq.result.confidence < low_confidence_threshold
