from datetime import datetime

import pytest
from groundlight import Groundlight
from groundlight.images import jpeg_from_file
from openapi_client.model.detector import Detector


@pytest.fixture
def gl() -> Groundlight:
    return Groundlight(endpoint="http://localhost:8000/device-api")


@pytest.fixture
def detector(gl: Groundlight) -> Detector:
    name = f"Test {datetime.utcnow()}"  # Need a unique name
    query = "Test query?"
    return gl.create_detector(name=name, query=query)


@pytest.mark.skip(reason="We don't want to create a million detectors")
def test_create_detector(gl: Groundlight):
    name = f"Test {datetime.utcnow()}"  # Need a unique name
    query = "Test query?"
    detector = gl.create_detector(name=name, query=query)
    assert str(detector)


def test_list_detectors(gl: Groundlight):
    detectors = gl.list_detectors()
    assert str(detectors)


@pytest.mark.skip(reason="We don't want to create a million detectors")
def test_get_detector(gl: Groundlight, detector: Detector):
    detector = gl.get_detector(id=detector.id)
    assert str(detector)


def test_submit_image_query(gl: Groundlight):
    image_bytesio = jpeg_from_file("test/assets/dog.jpeg")
    image_query = gl.submit_image_query(detector_id="det_28oN8XiaZOdhXd8uZPgosivDbvl", image_bytesio=image_bytesio)
    assert str(image_query)


def test_list_image_queries(gl: Groundlight):
    image_queries = gl.list_image_queries()
    assert str(image_queries)


def test_get_image_query(gl: Groundlight):
    image_query = gl.get_image_query(id="chk_28rFntQZjhQ7a1przsPMConQ6XL")
    assert str(image_query)
