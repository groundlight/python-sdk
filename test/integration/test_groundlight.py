from datetime import datetime

import openapi_client
import pytest
from groundlight import Groundlight
from groundlight.optional_imports import *
from model import Detector, ImageQuery, PaginatedDetectorList, PaginatedImageQueryList


@pytest.fixture
def gl() -> Groundlight:
    """Creates a Groundlight client object for testing."""
    gl = Groundlight()
    gl.DEFAULT_WAIT = 0.1
    return gl


@pytest.fixture
def detector(gl: Groundlight) -> Detector:
    """Creates a new Test detector."""
    name = f"Test {datetime.utcnow()}"  # Need a unique name
    query = "Test query?"
    return gl.create_detector(name=name, query=query)


@pytest.fixture
def image_query(gl: Groundlight, detector: Detector) -> ImageQuery:
    iq = gl.submit_image_query(detector=detector.id, image="test/assets/dog.jpeg")
    return iq


def test_create_detector(gl: Groundlight):
    name = f"Test {datetime.utcnow()}"  # Need a unique name
    query = "Test query?"
    _detector = gl.create_detector(name=name, query=query)
    assert str(_detector)
    assert isinstance(_detector, Detector)
    assert (
        _detector.confidence_threshold == Groundlight.DEFAULT_CONFIDENCE_THRESHOLD
    ), "We expected the default confidence threshold to be used."


def test_create_detector_with_config_name(gl: Groundlight):
    # "never-review" is a special model that always returns the same result with 100% confidence.
    # It's useful for testing.
    name = f"Test never-review {datetime.utcnow()}"  # Need a unique name
    query = "Test query with never-review?"
    config_name = "never-review"
    _detector = gl.create_detector(name=name, query=query, config_name=config_name)
    assert str(_detector)
    assert isinstance(_detector, Detector)


def test_create_detector_with_confidence(gl: Groundlight):
    # "never-review" is a special model that always returns the same result with 100% confidence.
    # It's useful for testing.
    name = f"Test with confidence {datetime.utcnow()}"  # Need a unique name
    query = "Is there a dog in the image?"
    config_name = "never-review"
    confidence = 0.825
    _detector = gl.create_detector(name=name, query=query, confidence=confidence, config_name=config_name)
    assert str(_detector)
    assert isinstance(_detector, Detector)
    assert _detector.confidence_threshold == confidence

    # If you retrieve an existing detector, we currently require the confidence and query to match
    # exactly. TODO: We may want to allow updating those fields through the SDK (and then we can
    # change this test).
    different_confidence = 0.7
    with pytest.raises(ValueError):
        gl.get_or_create_detector(name=name, query=query, confidence=different_confidence, config_name=config_name)

    different_query = "Bad bad bad?"
    with pytest.raises(ValueError):
        gl.get_or_create_detector(name=name, query=different_query, confidence=confidence, config_name=config_name)

    # If the confidence is not provided, we will use the existing detector's confidence.
    retrieved_detector = gl.get_or_create_detector(name=name, query=query)
    assert (
        retrieved_detector.confidence_threshold == confidence
    ), "We expected to retrieve the existing detector's confidence, but got a different value."


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


@pytest.mark.skipif(MISSING_PIL, reason="Needs pillow")
def test_submit_image_query_pil(gl: Groundlight, detector: Detector):
    # generates a pil image and submits it
    from PIL import Image

    dog = Image.open("test/assets/dog.jpeg")
    _image_query = gl.submit_image_query(detector=detector.id, image=dog)

    black = Image.new("RGB", (640, 480))
    _image_query = gl.submit_image_query(detector=detector.id, image=black)


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
    # TODO: Fully deprecate chk_ prefix
    assert iqid.startswith("chk_") or iqid.startswith("iq_")
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
