from datetime import datetime

import pytest
from groundlight import Groundlight
from openapi_client.model.detector import Detector


@pytest.fixture
def gl() -> Groundlight:
    return Groundlight(endpoint="http://localhost:8000/device-api")


@pytest.fixture
def detector(gl: Groundlight) -> Detector:
    name = f"Test {datetime.utcnow()}"  # Need a unique name
    query = "Test query?"
    response = gl.create_detector(body={"name": name, "query": query})
    return response.body


@pytest.mark.skip(reason="We don't want to create a million detectors")
def test_create_detector(gl: Groundlight):
    name = f"Test {datetime.utcnow()}"  # Need a unique name
    query = "Test query?"
    detector = gl.create_detector({"name": name, "query": query}).body
    assert str(detector)


def test_list_detectors(gl: Groundlight):
    detectors = gl.list_detectors().body
    assert str(detectors)


@pytest.mark.skip(reason="We don't want to create a million detectors")
def test_get_detector(gl: Groundlight, detector: Detector):
    detector = gl.get_detector({"id": detector.id}).body
    assert str(detector)


@pytest.mark.xfail(reason="This doesn't work yet - we have to fix the content_type handling")
def test_submit_image_query(gl: Groundlight):
    image_query = gl.submit_image_query(body=b"", query_params={"detector_id": ""}, content_type="image/jpeg").body
    assert str(image_query)


def test_list_image_queries(gl: Groundlight):
    image_queries = gl.list_image_queries().body
    assert str(image_queries)


def test_get_image_query(gl: Groundlight):
    image_query = gl.get_image_query({"id": "chk_28rFntQZjhQ7a1przsPMConQ6XL"}).body
    assert str(image_query)
