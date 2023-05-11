# Optional star-imports are weird and not usually recommended ...
# ruff: noqa: F403,F405
# pylint: disable=wildcard-import,unused-wildcard-import,redefined-outer-name,import-outside-toplevel
from datetime import datetime
from typing import Any

import openapi_client
import pytest

from groundlight import Groundlight
from groundlight.binary_labels import VALID_DISPLAY_LABELS, DeprecatedLabel, Label, convert_internal_label_to_display
from groundlight.internalapi import NotFoundError
from groundlight.optional_imports import *
from groundlight.status_codes import is_user_error
from model import ClassificationResult, Detector, ImageQuery, PaginatedDetectorList, PaginatedImageQueryList

DEFAULT_CONFIDENCE_THRESHOLD = 0.9

def is_valid_display_result(result: Any) -> bool:
    """Is the image query result valid to display to the user?."""
    if not isinstance(result, ClassificationResult):
        return False
    if not is_valid_display_label(result.label):
        return False
    return True


def is_valid_display_label(label: str) -> bool:
    """Is the image query result label valid to display to the user?."""
    # NOTE: For now, we strictly only show UPPERCASE labels to the user.
    return label in VALID_DISPLAY_LABELS


@pytest.fixture(name="gl")
def fixture_gl() -> Groundlight:
    """Creates a Groundlight client object for testing."""
    _gl = Groundlight()
    _gl.DEFAULT_WAIT = 0.1
    return _gl


@pytest.fixture(name="detector")
def fixture_detector(gl: Groundlight) -> Detector:
    """Creates a new Test detector."""
    name = f"Test {datetime.utcnow()}"  # Need a unique name
    query = "Is there a dog?"
    return gl.create_detector(name=name, query=query)


@pytest.fixture(name="image_query")
def fixture_image_query(gl: Groundlight, detector: Detector) -> ImageQuery:
    iq = gl.submit_image_query(detector=detector.id, image="test/assets/dog.jpeg")
    return iq


def test_create_detector(gl: Groundlight):
    name = f"Test {datetime.utcnow()}"  # Need a unique name
    query = "Is there a dog?"
    _detector = gl.create_detector(name=name, query=query)
    assert str(_detector)
    assert isinstance(_detector, Detector)
    assert (
        _detector.confidence_threshold == DEFAULT_CONFIDENCE_THRESHOLD
    ), "We expected the default confidence threshold to be used."


def test_create_detector_with_config_name(gl: Groundlight):
    # "never-review" is a special model that always returns the same result with 100% confidence.
    # It's useful for testing.
    name = f"Test never-review {datetime.utcnow()}"  # Need a unique name
    query = "Is there a dog (never-review)?"
    config_name = "never-review"
    _detector = gl.create_detector(name=name, query=query, config_name=config_name)
    assert str(_detector)
    assert isinstance(_detector, Detector)


def test_create_detector_with_confidence_threshold(gl: Groundlight):
    # "never-review" is a special model that always returns the same result with 100% confidence.
    # It's useful for testing.
    name = f"Test with confidence {datetime.utcnow()}"  # Need a unique name
    query = "Is there a dog in the image?"
    config_name = "never-review"
    confidence_threshold = 0.825
    _detector = gl.create_detector(
        name=name,
        query=query,
        confidence_threshold=confidence_threshold,
        config_name=config_name,
    )
    assert str(_detector)
    assert isinstance(_detector, Detector)
    assert _detector.confidence_threshold == confidence_threshold

    # If you retrieve an existing detector, we currently require the confidence and query to match
    # exactly. TODO: We may want to allow updating those fields through the SDK (and then we can
    # change this test).
    different_confidence = 0.7
    with pytest.raises(ValueError):
        gl.get_or_create_detector(
            name=name,
            query=query,
            confidence_threshold=different_confidence,
            config_name=config_name,
        )

    different_query = "Bad bad bad?"
    with pytest.raises(ValueError):
        gl.get_or_create_detector(
            name=name,
            query=different_query,
            confidence_threshold=confidence_threshold,
            config_name=config_name,
        )

    # If the confidence is not provided, we will use the existing detector's confidence.
    retrieved_detector = gl.get_or_create_detector(name=name, query=query)
    assert (
        retrieved_detector.confidence_threshold == confidence_threshold
    ), "We expected to retrieve the existing detector's confidence, but got a different value."


def test_list_detectors(gl: Groundlight):
    detectors = gl.list_detectors()
    assert str(detectors)
    assert isinstance(detectors, PaginatedDetectorList)


def test_get_or_create_detector(gl: Groundlight):
    # With a unique name, we should be creating a new detector.
    unique_name = f"Unique name {datetime.utcnow()}"
    query = "Is there a dog?"
    detector = gl.get_or_create_detector(name=unique_name, query=query)
    assert str(detector)
    assert isinstance(detector, Detector)

    # If we try to create a detector with the same name, we should get the same detector back.
    retrieved_detector = gl.get_or_create_detector(name=unique_name, query=query)
    assert retrieved_detector.id == detector.id


def test_get_detector(gl: Groundlight, detector: Detector):
    _detector = gl.get_detector(id=detector.id)
    assert str(_detector)
    assert isinstance(_detector, Detector)


def test_get_detector_by_name(gl: Groundlight, detector: Detector):
    _detector = gl.get_detector_by_name(name=detector.name)
    assert str(_detector)
    assert isinstance(_detector, Detector)
    assert _detector.id == detector.id

    with pytest.raises(NotFoundError):
        gl.get_detector_by_name(name="not a real name")


def test_submit_image_query_blocking(gl: Groundlight, detector: Detector):
    # Ask for a trivially small wait so it never has time to update, but uses the code path
    _image_query = gl.submit_image_query(detector=detector.id, image="test/assets/dog.jpeg", wait=2)
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)
    assert is_valid_display_result(_image_query.result)


def test_submit_image_query_returns_yes(gl: Groundlight):
    # We use the "never-review" model to guarantee a "yes" answer.
    detector = gl.get_or_create_detector(name="Always a dog", query="Is there a dog?", config_name="never-review")
    image_query = gl.submit_image_query(detector=detector, image="test/assets/dog.jpeg", wait=5)
    assert image_query.result.label == Label.YES


def test_submit_image_query_filename(gl: Groundlight, detector: Detector):
    _image_query = gl.submit_image_query(detector=detector.id, image="test/assets/dog.jpeg")
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)
    assert is_valid_display_result(_image_query.result)


def test_submit_image_query_jpeg_bytes(gl: Groundlight, detector: Detector):
    jpeg = open("test/assets/dog.jpeg", "rb").read()
    _image_query = gl.submit_image_query(detector=detector.id, image=jpeg)
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)
    assert is_valid_display_result(_image_query.result)


def test_submit_image_query_jpeg_truncated(gl: Groundlight, detector: Detector):
    jpeg = open("test/assets/dog.jpeg", "rb").read()
    jpeg_truncated = jpeg[:-500]  # Cut off the last 500 bytes
    # This is an extra difficult test because the header is valid.
    # So a casual check of the image will appear valid.
    with pytest.raises(openapi_client.exceptions.ApiException) as exc_info:
        _image_query = gl.submit_image_query(detector=detector.id, image=jpeg_truncated)
    exc_value = exc_info.value
    assert is_user_error(exc_value.status)


def test_submit_image_query_bad_filename(gl: Groundlight, detector: Detector):
    with pytest.raises(FileNotFoundError):
        _image_query = gl.submit_image_query(detector=detector.id, image="missing-file.jpeg")


def test_submit_image_query_bad_jpeg_file(gl: Groundlight, detector: Detector):
    with pytest.raises(ValueError) as exc_info:
        _image_query = gl.submit_image_query(detector=detector.id, image="test/assets/blankfile.jpeg")
    assert "jpeg" in str(exc_info).lower()


@pytest.mark.skipif(MISSING_PIL, reason="Needs pillow")  # type: ignore
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

    if image_queries.results:
        for image_query in image_queries.results:
            assert str(image_query)
            assert isinstance(image_query, ImageQuery)
            assert is_valid_display_result(image_query.result)


def test_get_image_query(gl: Groundlight, image_query: ImageQuery):
    _image_query = gl.get_image_query(id=image_query.id)
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)
    assert is_valid_display_result(_image_query.result)


def test_get_image_query_label_yes(gl: Groundlight, image_query: ImageQuery):
    gl.add_label(image_query, Label.YES)
    retrieved_iq = gl.get_image_query(id=image_query.id)
    assert retrieved_iq.result.label == Label.YES


def test_get_image_query_label_no(gl: Groundlight, image_query: ImageQuery):
    gl.add_label(image_query, Label.NO)
    retrieved_iq = gl.get_image_query(id=image_query.id)
    assert retrieved_iq.result.label == Label.NO


def test_add_label_to_object(gl: Groundlight, image_query: ImageQuery):
    assert isinstance(image_query, ImageQuery)
    gl.add_label(image_query, Label.YES)


def test_add_label_by_id(gl: Groundlight, image_query: ImageQuery):
    iqid = image_query.id
    # TODO: Fully deprecate chk_ prefix
    assert iqid.startswith(("chk_", "iq_"))
    gl.add_label(iqid, Label.NO)


def test_add_label_names(gl: Groundlight, image_query: ImageQuery):
    iqid = image_query.id

    # Valid labels
    gl.add_label(iqid, Label.YES)
    gl.add_label(iqid, Label.YES.value)
    gl.add_label(iqid, "YES")
    gl.add_label(iqid, "yes")
    gl.add_label(iqid, "yEs")
    gl.add_label(iqid, Label.NO)
    gl.add_label(iqid, Label.NO.value)
    gl.add_label(iqid, "NO")
    gl.add_label(iqid, "no")

    # Invalid labels
    with pytest.raises(ValueError):
        gl.add_label(iqid, "PASS")
    with pytest.raises(ValueError):
        gl.add_label(iqid, "FAIL")
    with pytest.raises(ValueError):
        gl.add_label(iqid, DeprecatedLabel.PASS)
    with pytest.raises(ValueError):
        gl.add_label(iqid, DeprecatedLabel.FAIL)
    with pytest.raises(ValueError):
        gl.add_label(iqid, "sorta")
    with pytest.raises(ValueError):
        gl.add_label(iqid, "YES ")
    with pytest.raises(ValueError):
        gl.add_label(iqid, " YES")
    with pytest.raises(ValueError):
        gl.add_label(iqid, "0")
    with pytest.raises(ValueError):
        gl.add_label(iqid, "1")

    # We technically don't allow these in the type signature, but users might do it anyway
    with pytest.raises(ValueError):
        gl.add_label(iqid, 0)  # type: ignore
    with pytest.raises(ValueError):
        gl.add_label(iqid, 1)  # type: ignore
    with pytest.raises(ValueError):
        gl.add_label(iqid, None)  # type: ignore
    with pytest.raises(ValueError):
        gl.add_label(iqid, True)  # type: ignore
    with pytest.raises(ValueError):
        gl.add_label(iqid, False)  # type: ignore
    with pytest.raises(ValueError):
        gl.add_label(iqid, b"YES")  # type: ignore

    # We may want to support something like this in the future, but not yet
    with pytest.raises(ValueError):
        gl.add_label(iqid, Label.UNSURE)


def test_label_conversion_produces_strings():
    # In our code, it's easier to work with enums, but we allow users to pass in strings or enums
    labels = ["YES", Label.YES, Label.YES.value, "NO", Label.NO, Label.NO.value]
    for label in labels:
        display = convert_internal_label_to_display("", label)
        assert isinstance(display, str)
        internal = convert_internal_label_to_display("", display)
        assert isinstance(internal, str)


def test_enum_string_equality():
    assert "YES" == Label.YES == Label.YES.value


@pytest.mark.skipif(MISSING_NUMPY or MISSING_PIL, reason="Needs numpy and pillow")  # type: ignore
def test_submit_numpy_image(gl: Groundlight, detector: Detector):
    np_img = np.random.uniform(0, 255, (600, 800, 3))  # type: ignore
    _image_query = gl.submit_image_query(detector=detector.id, image=np_img)
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)
    assert is_valid_display_result(_image_query.result)
