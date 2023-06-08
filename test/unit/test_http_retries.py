import pytest
import requests_mock
from groundlight import Groundlight
from model import Detector

DEFAULT_CONFIDENCE_THRESHOLD = 0.9
DETECTOR_NAME = "test detector"
TOTAL_RETRIES = 4


@pytest.fixture(name="gl")
def groundlight_fixture() -> Groundlight:
    "Creates a Groundlight client"
    gl = Groundlight()
    gl.DEFAULT_WAIT
    return gl


@pytest.fixture(name="detector")
def detector_fixture(gl: Groundlight) -> Detector:
    """Creates a new test detector"""
    return gl.get_or_create_detector(
        name="Test detector", query="Is there a dog?", confidence_threshold=DEFAULT_CONFIDENCE_THRESHOLD
    )


def test_get_detector_by_name_attempts_retries(gl: Groundlight):
    """Tests that call to `get_detector_by_name` retries to establish
    a HTTP connection in case of a 500-599 response.
    Here we are forcing the "execution" of requests.request to always 
    return a status error code in range [500, 599]
    """
    status_codes = range(500, 600)
    url = "https://api.groundlight.ai/device-api/v1/detectors?name=Test detector"

    for status_code in status_codes:
        with requests_mock.Mocker() as m:
            m.get(url, status_code=status_code)

            with pytest.raises(RuntimeError):
                gl.get_detector_by_name(name="Test detector")

            assert m.call_count == TOTAL_RETRIES + 1


def test_add_label_attempts_retries(gl: Groundlight):
    pass 
