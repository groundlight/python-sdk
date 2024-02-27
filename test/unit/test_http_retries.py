from datetime import datetime
from typing import Any, Callable
from unittest import mock

import pytest
from groundlight import Groundlight
from groundlight.binary_labels import Label
from groundlight.internalapi import InternalApiError
from model import Detector

DEFAULT_CONFIDENCE_THRESHOLD = 0.9
DETECTOR_NAME = f"test detector_{datetime.utcnow().strftime('%Y=%m-%d %H:%M:%S')}"
TOTAL_RETRIES = 3
STATUS_CODES = range(500, 505)
IMAGE_FILE = "test/assets/dog.jpeg"


@pytest.fixture(name="gl")
def groundlight_fixture() -> Groundlight:
    "Creates a Groundlight client"
    gl = Groundlight()
    return gl


@pytest.fixture(name="detector")
def detector_fixture(gl: Groundlight) -> Detector:
    return gl.get_or_create_detector(
        name=DETECTOR_NAME, query="Is there a dog?", confidence_threshold=DEFAULT_CONFIDENCE_THRESHOLD
    )


def test_create_detector_attempts_retries(gl: Groundlight):
    run_test(
        mocked_call="urllib3.PoolManager.request",
        api_method=gl.create_detector,
        expected_call_counts=TOTAL_RETRIES + 1,
        name=DETECTOR_NAME,
        query="Is there a dog?",
        confidence_threshold=DEFAULT_CONFIDENCE_THRESHOLD,
    )


def test_get_or_create_detector_attempts_retries(gl: Groundlight):
    run_test(
        mocked_call="requests.request",
        api_method=gl.get_or_create_detector,
        expected_call_counts=TOTAL_RETRIES + 1,
        name=DETECTOR_NAME,
        query="Is there a dog?",
        confidence_threshold=DEFAULT_CONFIDENCE_THRESHOLD,
    )


# @flaky(max_runs=4, min_passes=1)
def test_get_detector_attempts_retries(gl: Groundlight, detector: Detector):
    run_test(
        mocked_call="urllib3.PoolManager.request",
        api_method=gl.get_detector,
        expected_call_counts=TOTAL_RETRIES + 1,
        id=detector.id,
    )


def test_get_detector_by_name_attempts_retries(gl: Groundlight):
    run_test(
        mocked_call="requests.request",
        api_method=gl.get_detector_by_name,
        expected_call_counts=TOTAL_RETRIES + 1,
        name=DETECTOR_NAME,
    )


def test_list_detectors_attempts_retries(gl: Groundlight):
    run_test(
        mocked_call="urllib3.PoolManager.request", api_method=gl.list_detectors, expected_call_counts=TOTAL_RETRIES + 1
    )


def test_submit_image_query_attempts_retries(gl: Groundlight):
    run_test(
        mocked_call="urllib3.PoolManager.request",
        api_method=gl.submit_image_query,
        expected_call_counts=TOTAL_RETRIES + 1,
        detector=DETECTOR_NAME,
        image=IMAGE_FILE,
        wait=1,
    )


def test_get_image_query_attempts_retries(gl: Groundlight, detector: Detector):
    image_query = gl.submit_image_query(detector=detector.id, image=IMAGE_FILE)

    run_test(
        mocked_call="urllib3.PoolManager.request",
        api_method=gl.get_image_query,
        expected_call_counts=TOTAL_RETRIES + 1,
        id=image_query.id,
    )


def test_list_image_queries_attempts_retries(gl: Groundlight):
    run_test(
        mocked_call="urllib3.PoolManager.request",
        api_method=gl.list_image_queries,
        expected_call_counts=TOTAL_RETRIES + 1,
    )


def test_add_label_attempts_retries(gl: Groundlight, detector: Detector):
    image_query = gl.submit_image_query(detector=detector.id, image=IMAGE_FILE)
    run_test(
        mocked_call="requests.request",
        api_method=gl.add_label,
        expected_call_counts=TOTAL_RETRIES + 1,
        image_query=image_query,
        label=Label.YES,
    )

    run_test(
        mocked_call="requests.request",
        api_method=gl.add_label,
        expected_call_counts=TOTAL_RETRIES + 1,
        image_query=image_query,
        label="NO",
    )


def run_test(mocked_call: str, api_method: Callable[..., Any], expected_call_counts: int, **kwargs):
    with mock.patch(mocked_call) as mock_request:
        for status_code in STATUS_CODES:
            mock_request.return_value.status = status_code

            with pytest.raises(InternalApiError):
                api_method(**kwargs)

            assert mock_request.call_count == expected_call_counts
            mock_request.reset_mock()


def test_submit_image_query_succeeds_after_retry(gl: Groundlight, detector: Detector):
    # TODO: figure out a good way to test `submit_image_query` such that it fails
    # the first few times, but eventually succeeds.
    pass
