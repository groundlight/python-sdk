import os
from datetime import datetime

import pytest
from groundlight import Groundlight
from model import Detector, ImageQuery, PaginatedDetectorList, PaginatedImageQueryList


@pytest.fixture
def gl() -> Groundlight:
    endpoint = os.environ.get("GROUNDLIGHT_TEST_API_ENDPOINT", "http://localhost:8000/device-api")
    return Groundlight(endpoint=endpoint)


@pytest.fixture
def detector(gl: Groundlight) -> Detector:
    name = f"Test {datetime.utcnow()}"  # Need a unique name
    query = "Test query?"
    return gl.create_detector(name=name, query=query)


@pytest.fixture
def image_query(gl: Groundlight, detector: Detector) -> ImageQuery:
    return gl.submit_image_query(detector=detector.id, image="test/assets/dog.jpeg")


# @pytest.mark.skip(reason="We don't want to create a million detectors")
def test_create_detector(gl: Groundlight):
    name = f"Test {datetime.utcnow()}"  # Need a unique name
    query = "Test query?"
    _detector = gl.create_detector(name=name, query=query)
    assert str(_detector)
    assert isinstance(_detector, Detector)


# @pytest.mark.skip(reason="We don't want to create a million detectors")
def test_create_detector_with_config_name(gl: Groundlight):
    name = f"Test b4mu11-mlp {datetime.utcnow()}"  # Need a unique name
    query = "Test query with b4mu11-mlp?"
    config_name = "b4mu11-mlp"
    _detector = gl.create_detector(name=name, query=query, config_name=config_name)
    assert str(_detector)
    assert isinstance(_detector, Detector)


def test_list_detectors(gl: Groundlight):
    detectors = gl.list_detectors()
    assert str(detectors)
    assert isinstance(detectors, PaginatedDetectorList)


# @pytest.mark.skip(reason="We don't want to create a million detectors")
def test_get_detector(gl: Groundlight, detector: Detector):
    _detector = gl.get_detector(id=detector.id)
    assert str(_detector)
    assert isinstance(_detector, Detector)


# @pytest.mark.skip(reason="We don't want to create a million detectors and image_queries")
def test_submit_image_query(gl: Groundlight, detector: Detector):
    _image_query = gl.submit_image_query(detector=detector.id, image="test/assets/dog.jpeg")
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)


def test_list_image_queries(gl: Groundlight):
    image_queries = gl.list_image_queries()
    assert str(image_queries)
    assert isinstance(image_queries, PaginatedImageQueryList)


# @pytest.mark.skip(reason="We don't want to create a million detectors and image_queries")
def test_get_image_query(gl: Groundlight, image_query: ImageQuery):
    _image_query = gl.get_image_query(id=image_query.id)
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)


try:
    import numpy as np

    NUMPY_MISSING = False
except ImportError:
    NUMPY_MISSING = True

try:
    import PIL

    PIL_MISSING = False
except ImportError:
    PIL_MISSING = True


#@pytest.mark.skipif(NUMPY_MISSING or PIL_MISSING, reason="Needs numpy and pillow")
def test_submit_numpy_image(gl: Groundlight, detector: Detector):
    np_img = np.random.uniform(0, 255, (600, 800, 3))
    _image_query = gl.submit_image_query(detector=detector.id, image=np_img)
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)
