import os
from datetime import datetime

import openapi_client
import pytest
from model import Detector, ImageQuery, PaginatedDetectorList, PaginatedImageQueryList

from groundlight import Groundlight
from groundlight.optional_imports import *


@pytest.fixture
def gl() -> Groundlight:
    """Creates a Groundlight client object for testing."""
    return Groundlight()


@pytest.fixture
def detector(gl: Groundlight) -> Detector:
    """Creates a new Test detector."""
    name = f"Test {datetime.utcnow()}"  # Need a unique name
    query = "Test query?"
    return gl.create_detector(name=name, query=query)


@pytest.fixture
def image_query(gl: Groundlight, detector: Detector) -> ImageQuery:
    return gl.submit_image_query(detector=detector.id, image="test/assets/dog.jpeg")


def test_create_detector(gl: Groundlight):
    name = f"Test {datetime.utcnow()}"  # Need a unique name
    query = "Test query?"
    _detector = gl.create_detector(name=name, query=query)
    assert str(_detector)
    assert isinstance(_detector, Detector)


def test_create_detector_with_config_name(gl: Groundlight):
    # "never-review" is a special model that always returns the same result with 100% confidence.
    # It's useful for testing.
    name = f"Test never-review {datetime.utcnow()}"  # Need a unique name
    query = "Test query with never-review?"
    config_name = "never-review"
    _detector = gl.create_detector(name=name, query=query, config_name=config_name)
    assert str(_detector)
    assert isinstance(_detector, Detector)


def test_list_detectors(gl: Groundlight):
    detectors = gl.list_detectors()
    assert str(detectors)
    assert isinstance(detectors, PaginatedDetectorList)


def test_get_detector(gl: Groundlight, detector: Detector):
    _detector = gl.get_detector(id=detector.id)
    assert str(_detector)
    assert isinstance(_detector, Detector)


def test_submit_image_query_blocking(gl: Groundlight, detector: Detector):
    # Ask for a trivially small wait so it never has time to update, but uses the code path
    _image_query = gl.submit_image_query(detector=detector.id, image="test/assets/dog.jpeg", wait=2)
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)


def test_submit_image_query_filename(gl: Groundlight, detector: Detector):
    _image_query = gl.submit_image_query(detector=detector.id, image="test/assets/dog.jpeg")
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)


def test_submit_image_query_jpeg_bytes(gl: Groundlight, detector: Detector):
    jpeg = open("test/assets/dog.jpeg", "rb").read()
    _image_query = gl.submit_image_query(detector=detector.id, image=jpeg)
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)


def test_submit_image_query_jpeg_truncated(gl: Groundlight, detector: Detector):
    jpeg = open("test/assets/dog.jpeg", "rb").read()
    jpeg_truncated = jpeg[:-500]  # Cut off the last 500 bytes
    # This is an extra difficult test because the header is valid.
    # So a casual check of the image will appear valid.
    with pytest.raises(openapi_client.exceptions.ApiException) as exc_info:
        _image_query = gl.submit_image_query(detector=detector.id, image=jpeg_truncated)
    e = exc_info.value
    assert e.status == 400


def test_submit_image_query_bad_filename(gl: Groundlight, detector: Detector):
    with pytest.raises(FileNotFoundError):
        _image_query = gl.submit_image_query(detector=detector.id, image="missing-file.jpeg")


def test_submit_image_query_bad_jpeg_file(gl: Groundlight, detector: Detector):
    with pytest.raises(ValueError) as exc_info:
        _image_query = gl.submit_image_query(detector=detector.id, image="test/assets/blankfile.jpeg")
    assert "jpeg" in str(exc_info).lower()


def test_list_image_queries(gl: Groundlight):
    image_queries = gl.list_image_queries()
    assert str(image_queries)
    assert isinstance(image_queries, PaginatedImageQueryList)


def test_get_image_query(gl: Groundlight, image_query: ImageQuery):
    _image_query = gl.get_image_query(id=image_query.id)
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)


def test_add_label_to_object(gl: Groundlight, image_query: ImageQuery):
    assert isinstance(image_query, ImageQuery)
    gl.add_label(image_query, "Yes")


def test_add_label_by_id(gl: Groundlight, image_query: ImageQuery):
    iqid = image_query.id
    assert iqid.startswith("iq_")
    gl.add_label(iqid, "No")


def test_add_label_names(gl: Groundlight, image_query: ImageQuery):
    iqid = image_query.id
    gl.add_label(iqid, "FAIL")
    gl.add_label(iqid, "PASS")
    gl.add_label(iqid, "Yes")
    gl.add_label(iqid, "No")
    with pytest.raises(ValueError):
        gl.add_label(iqid, "sorta")


@pytest.mark.skipif(MISSING_NUMPY or MISSING_PIL, reason="Needs numpy and pillow")
def test_submit_numpy_image(gl: Groundlight, detector: Detector):
    np_img = np.random.uniform(0, 255, (600, 800, 3))
    _image_query = gl.submit_image_query(detector=detector.id, image=np_img)
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)
