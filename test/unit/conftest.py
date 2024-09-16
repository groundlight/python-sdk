from datetime import datetime

import pytest
from groundlight import ExperimentalApi, Groundlight
from model import Detector, ImageQuery


def pytest_configure(config):
    # Run environment check before tests
    gl = Groundlight()
    if gl._user_is_privileged():
        raise Exception(
            "ERROR: You are running tests with a privileged user. Please run tests with a non-privileged user."
        )


@pytest.fixture(name="gl")
def fixture_gl() -> Groundlight:
    """Creates a Groundlight client object for testing."""
    _gl = Groundlight()
    _gl.DEFAULT_WAIT = 10
    return _gl


@pytest.fixture(name="detector")
def fixture_detector(gl: Groundlight) -> Detector:
    """Creates a new Test detector."""
    name = f"Test {datetime.utcnow()}"  # Need a unique name
    query = "Is there a dog?"
    pipeline_config = "never-review"
    return gl.create_detector(name=name, query=query, pipeline_config=pipeline_config)


@pytest.fixture(name="image_query_yes")
def fixture_image_query_yes(gl: Groundlight, detector: Detector) -> ImageQuery:
    iq = gl.submit_image_query(detector=detector.id, image="test/assets/dog.jpeg", human_review="NEVER")
    return iq


@pytest.fixture(name="image_query_no")
def fixture_image_query_no(gl: Groundlight, detector: Detector) -> ImageQuery:
    iq = gl.submit_image_query(detector=detector.id, image="test/assets/cat.jpeg", human_review="NEVER")
    return iq


@pytest.fixture(name="gl_experimental")
def _gl() -> ExperimentalApi:
    return ExperimentalApi()
