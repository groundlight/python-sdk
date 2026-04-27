from datetime import datetime
from typing import Callable
from uuid import uuid4

import pytest
from groundlight import ExperimentalApi, Groundlight
from model import Detector, ImageQuery, ImageQueryTypeEnum, ResultTypeEnum


def _generate_unique_detector_name(prefix: str = "Test") -> str:
    """Generates a detector name with a timestamp and random suffix to ensure uniqueness."""
    return f"{prefix} {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}_{uuid4().hex[:8]}"


@pytest.fixture(name="detector_name")
def fixture_detector_name() -> Callable[..., str]:
    """Fixture that provides a callable to generate unique detector names."""
    return _generate_unique_detector_name


def pytest_configure(config):  # pylint: disable=unused-argument
    # Run environment check before tests
    gl = Groundlight()
    if gl._user_is_privileged():  # pylint: disable=protected-access
        raise RuntimeError(
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
    query = "Is there a dog?"
    pipeline_config = "never-review"
    return gl.create_detector(name=_generate_unique_detector_name(), query=query, pipeline_config=pipeline_config)


@pytest.fixture(name="count_detector")
def fixture_count_detector(gl_experimental: ExperimentalApi) -> Detector:
    """Creates a new Test detector."""
    query = "How many dogs?"
    pipeline_config = "never-review-multi"  # always predicts 0
    return gl_experimental.create_counting_detector(
        name=_generate_unique_detector_name(), query=query, class_name="dog", pipeline_config=pipeline_config
    )


@pytest.fixture(name="image_query_yes")
def fixture_image_query_yes(gl: Groundlight, detector: Detector) -> ImageQuery:
    iq = gl.submit_image_query(detector=detector.id, image="test/assets/dog.jpeg", human_review="NEVER")
    return iq


@pytest.fixture(name="image_query_no")
def fixture_image_query_no(gl: Groundlight, detector: Detector) -> ImageQuery:
    iq = gl.submit_image_query(detector=detector.id, image="test/assets/cat.jpeg", human_review="NEVER")
    return iq


@pytest.fixture(name="image_query_one")
def fixture_image_query_one(gl_experimental: Groundlight, count_detector: Detector) -> ImageQuery:
    iq = gl_experimental.submit_image_query(
        detector=count_detector.id, image="test/assets/dog.jpeg", human_review="NEVER"
    )
    return iq


@pytest.fixture(name="image_query_zero")
def fixture_image_query_zero(gl_experimental: Groundlight, count_detector: Detector) -> ImageQuery:
    iq = gl_experimental.submit_image_query(
        detector=count_detector.id, image="test/assets/no_dogs.jpeg", human_review="NEVER"
    )
    return iq


@pytest.fixture(name="gl_experimental")
def fixture_gl_experimental() -> ExperimentalApi:
    _gl = ExperimentalApi()
    _gl.DEFAULT_WAIT = 10
    return _gl


@pytest.fixture(name="initial_iq")
def fixture_initial_iq() -> ImageQuery:
    return ImageQuery(
        metadata=None,
        id="iq_fakeidhere",
        type=ImageQueryTypeEnum.image_query,
        created_at=datetime.utcnow(),
        query="Is there a dog?",
        detector_id="det_fakeidhere",
        result_type=ResultTypeEnum.binary_classification,
        result=None,
        patience_time=30,
        confidence_threshold=0.9,
        rois=None,
        text=None,
    )
