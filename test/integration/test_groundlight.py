# Optional star-imports are weird and not usually recommended ...
# ruff: noqa: F403,F405
# pylint: disable=wildcard-import,unused-wildcard-import,redefined-outer-name,import-outside-toplevel
from datetime import datetime
from typing import Any

import openapi_client
import pytest
from groundlight import Groundlight
from groundlight.binary_labels import VALID_DISPLAY_LABELS, DeprecatedLabel, Label, convert_internal_label_to_display
from groundlight.internalapi import InternalApiError, NotFoundError
from groundlight.optional_imports import *
from groundlight.status_codes import is_user_error
from image_transforms import ImageTransform
from model import ClassificationResult, Detector, ImageQuery, PaginatedDetectorList, PaginatedImageQueryList

DEFAULT_CONFIDENCE_THRESHOLD = 0.9
img_transform = ImageTransform()


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
    iq = gl.submit_image_query(detector=detector.id, image="test/assets/dog.jpeg")
    return iq


@pytest.fixture(name="image_query_no")
def fixture_image_query_no(gl: Groundlight, detector: Detector) -> ImageQuery:
    iq = gl.submit_image_query(detector=detector.id, image="test/assets/cat.jpeg")
    return iq


@pytest.fixture(name="augmented_image_query_yes")
def image_query_yes_with_augmentation(gl: Groundlight, detector: Detector) -> ImageQuery:
    image = "test/assets/dog.jpeg"
    # Flip and rotate
    transformed_image = Image.open(image).transpose(Image.FLIP_LEFT_RIGHT).rotate(45)

    iq = gl.submit_image_query(detector=detector.id, image=transformed_image)
    return iq


@pytest.fixture(name="augmented_image_query_no")
def image_query_no_with_augmentation(gl: Groundlight, detector: Detector) -> ImageQuery:
    image = "test/assets/cat.jpeg"
    # Flip and rotate
    transformed_image = Image.open(image).transpose(Image.FLIP_LEFT_RIGHT).rotate(45)

    iq = gl.submit_image_query(detector=detector.id, image=transformed_image)
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


def test_create_detector_with_pipeline_config(gl: Groundlight):
    # "never-review" is a special model that always returns the same result with 100% confidence.
    # It's useful for testing.
    name = f"Test never-review {datetime.utcnow()}"  # Need a unique name
    query = "Is there a dog (always-pass)?"
    pipeline_config = "never-review"
    _detector = gl.create_detector(name=name, query=query, pipeline_config=pipeline_config)
    assert str(_detector)
    assert isinstance(_detector, Detector)


def test_create_detector_with_confidence_threshold(gl: Groundlight):
    # "never-review" is a special model that always returns the same result with 100% confidence.
    # It's useful for testing.
    name = f"Test with confidence {datetime.utcnow()}"  # Need a unique name
    query = "Is there a dog in the image?"
    pipeline_config = "never-review"
    confidence_threshold = 0.825
    _detector = gl.create_detector(
        name=name,
        query=query,
        confidence_threshold=confidence_threshold,
        pipeline_config=pipeline_config,
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
            pipeline_config=pipeline_config,
        )

    different_query = "Bad bad bad?"
    with pytest.raises(ValueError):
        gl.get_or_create_detector(
            name=name,
            query=different_query,
            confidence_threshold=confidence_threshold,
            pipeline_config=pipeline_config,
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
    _image_query = gl.submit_image_query(detector=detector.id, image="test/assets/dog.jpeg", wait=10)
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)
    assert is_valid_display_result(_image_query.result)


def test_submit_image_query_returns_yes(gl: Groundlight):
    # We use the "never-review" pipeline to guarantee a confident "yes" answer.
    detector = gl.get_or_create_detector(name="Always a dog", query="Is there a dog?", pipeline_config="never-review")
    image_query = gl.submit_image_query(detector=detector, image="test/assets/dog.jpeg", wait=10)
    assert image_query.result.label == Label.YES


def test_submit_image_query_filename(gl: Groundlight, detector: Detector):
    _image_query = gl.submit_image_query(detector=detector.id, image="test/assets/dog.jpeg")
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)
    assert is_valid_display_result(_image_query.result)


def test_submit_image_query_with_human_review_param(gl: Groundlight, detector: Detector):
    # For now, this just tests that the image query is submitted successfully.
    # There should probably be a better way to check whether the image query was escalated for human review.

    for human_review_value in ("DEFAULT", "ALWAYS", "NEVER"):
        _image_query = gl.submit_image_query(
            detector=detector.id, image="test/assets/dog.jpeg", human_review=human_review_value
        )
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


def test_get_image_query(gl: Groundlight, image_query_yes: ImageQuery):
    _image_query = gl.get_image_query(id=image_query_yes.id)
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)
    assert is_valid_display_result(_image_query.result)


def test_get_image_query_label_yes(gl: Groundlight, detector: Detector):
    image = "test/assets/dog.jpeg"
    transformed_image = img_transform.random_rotate(Image.open(image))

    iq = gl.submit_image_query(detector=detector.id, image=transformed_image)

    gl.add_label(iq, Label.YES)
    retrieved_iq = gl.get_image_query(id=iq.id)
    assert retrieved_iq.result.label == Label.YES


def test_get_image_query_label_no(gl: Groundlight, detector: Detector):
    image = "test/assets/cat.jpeg"
    transformed_image = img_transform.random_shift(Image.open(image))
    iq = gl.submit_image_query(detector=detector.id, image=transformed_image)

    gl.add_label(iq, Label.NO)
    retrieved_iq = gl.get_image_query(id=iq.id)
    assert retrieved_iq.result.label == Label.NO


def test_add_label_to_object(gl: Groundlight, detector: Detector):
    image = "test/assets/dog.jpeg"
    transfomed_image = img_transform.random_shear(Image.open(image))
    iq = gl.submit_image_query(detector=detector.id, image=transfomed_image)

    assert isinstance(iq, ImageQuery)
    gl.add_label(iq, Label.YES)


def test_add_label_by_id(gl: Groundlight, detector: Detector):
    image = "test/assets/cat.jpeg"
    transformed_image = img_transform.random_scale(Image.open(image))
    iq = gl.submit_image_query(detector=detector.id, image=transformed_image)

    # TODO: Fully deprecate chk_ prefix
    assert iq.id.startswith(("chk_", "iq_"))
    gl.add_label(iq.id, Label.NO)


def test_add_label_names(gl: Groundlight, image_query_yes: ImageQuery, image_query_no: ImageQuery, detector: Detector):
    iqid_yes = image_query_yes.id
    iqid_no = image_query_no.id

    transformed_yes_image = img_transform.color_jitter(Image.open("test/assets/dog.jpeg"))
    transformed_no_image = img_transform.horizontal_flip(Image.open("test/assets/cat.jpeg"))
    
    iq_yes = gl.submit_image_query(detector=detector.id, image=transformed_yes_image)
    iq_no = gl.submit_image_query(detector=detector.id, image=transformed_no_image)

    iqid_yes, iqid_no = iq_yes.id, iq_no.id

    # Valid labels
    gl.add_label(iqid_yes, Label.YES)
    gl.add_label(iqid_yes, Label.YES.value)
    gl.add_label(iqid_yes, "YES")
    gl.add_label(iqid_yes, "yes")
    gl.add_label(iqid_yes, "yEs")
    gl.add_label(iqid_no, Label.NO)
    gl.add_label(iqid_no, Label.NO.value)
    gl.add_label(iqid_no, "NO")
    gl.add_label(iqid_no, "no")

    # Invalid labels
    with pytest.raises(ValueError):
        gl.add_label(iqid_yes, "PASS")
    with pytest.raises(ValueError):
        gl.add_label(iqid_yes, "FAIL")
    with pytest.raises(ValueError):
        gl.add_label(iqid_yes, DeprecatedLabel.PASS)
    with pytest.raises(ValueError):
        gl.add_label(iqid_yes, DeprecatedLabel.FAIL)
    with pytest.raises(ValueError):
        gl.add_label(iqid_yes, "sorta")
    with pytest.raises(ValueError):
        gl.add_label(iqid_yes, "YES ")
    with pytest.raises(ValueError):
        gl.add_label(iqid_yes, " YES")
    with pytest.raises(ValueError):
        gl.add_label(iqid_yes, "0")
    with pytest.raises(ValueError):
        gl.add_label(iqid_yes, "1")

    # We technically don't allow these in the type signature, but users might do it anyway
    with pytest.raises(ValueError):
        gl.add_label(iqid_yes, 0)  # type: ignore
    with pytest.raises(ValueError):
        gl.add_label(iqid_yes, 1)  # type: ignore
    with pytest.raises(ValueError):
        gl.add_label(iqid_yes, None)  # type: ignore
    with pytest.raises(ValueError):
        gl.add_label(iqid_yes, True)  # type: ignore
    with pytest.raises(ValueError):
        gl.add_label(iqid_yes, False)  # type: ignore
    with pytest.raises(ValueError):
        gl.add_label(iqid_yes, b"YES")  # type: ignore

    # We may want to support something like this in the future, but not yet
    with pytest.raises(ValueError):
        gl.add_label(iqid_yes, Label.UNSURE)


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


@pytest.mark.skipif(MISSING_PIL, reason="Needs pillow")  # type: ignore
def test_detector_improvement(gl: Groundlight):
    # test that we get confidence improvement after sending images in
    # Pass two of each type of image in
    import random
    import time

    from PIL import Image, ImageEnhance

    random.seed(2741)

    name = f"Test {datetime.utcnow()}"  # Need a unique name
    query = "Is there a dog?"
    detector = gl.create_detector(name=name, query=query)

    def submit_noisy_image(image, label=None):
        sharpness = ImageEnhance.Sharpness(image)
        noisy_image = sharpness.enhance(random.uniform(0.75, 1.25))
        color = ImageEnhance.Color(noisy_image)
        noisy_image = color.enhance(random.uniform(0.75, 1))
        contrast = ImageEnhance.Contrast(noisy_image)
        noisy_image = contrast.enhance(random.uniform(0.75, 1))
        brightness = ImageEnhance.Brightness(noisy_image)
        noisy_image = brightness.enhance(random.uniform(0.75, 1))
        img_query = gl.submit_image_query(detector=detector.id, image=noisy_image, wait=0)
        if label is not None:
            gl.add_label(img_query, label)
        return img_query

    dog = Image.open("test/assets/dog.jpeg")
    cat = Image.open("test/assets/cat.jpeg")

    submit_noisy_image(dog, "YES")
    submit_noisy_image(dog, "YES")
    submit_noisy_image(cat, "NO")
    submit_noisy_image(cat, "NO")

    # wait to give enough time to train
    wait_period = 30  # seconds
    num_wait_periods = 4  # 2 minutes total
    result_confidence = 0.6
    for _ in range(num_wait_periods):
        time.sleep(wait_period)
        new_dog_query = submit_noisy_image(dog)
        new_cat_query = submit_noisy_image(cat)
        new_cat_result_confidence = new_cat_query.result.confidence
        new_dog_result_confidence = new_dog_query.result.confidence

        if (
            new_cat_result_confidence and new_cat_result_confidence < result_confidence
        ) or new_cat_query.result.label == "YES":
            # If the new query is not confident enough, we'll try again
            continue
        elif (
            new_dog_result_confidence and new_dog_result_confidence < result_confidence
        ) or new_dog_query.result.label == "NO":
            # If the new query is not confident enough, we'll try again
            continue
        else:
            assert True
            return

    assert False, "The detector performance has not improved after two minutes"


def test_start_inspection(gl: Groundlight):
    inspection_id = gl.start_inspection()

    assert isinstance(inspection_id, str)
    assert "inspect_" in inspection_id


def test_update_inspection_metadata_success(gl: Groundlight):
    """Starts an inspection and adds a couple pieces of metadata to it.
    This should succeed. If there are any errors, an exception will be raised.
    """
    inspection_id = gl.start_inspection()

    user_provided_key = "Inspector"
    user_provided_value = "Bob"
    gl.update_inspection_metadata(inspection_id, user_provided_key, user_provided_value)

    user_provided_key = "Engine ID"
    user_provided_value = "1234"
    gl.update_inspection_metadata(inspection_id, user_provided_key, user_provided_value)


def test_update_inspection_metadata_failure(gl: Groundlight):
    """Attempts to add metadata to an inspection after it is closed.
    Should raise an exception.
    """
    inspection_id = gl.start_inspection()

    _ = gl.stop_inspection(inspection_id)

    with pytest.raises(ValueError):
        user_provided_key = "Inspector"
        user_provided_value = "Bob"
        gl.update_inspection_metadata(inspection_id, user_provided_key, user_provided_value)


def test_update_inspection_metadata_invalid_inspection_id(gl: Groundlight):
    """Attempt to update metadata for an inspection that doesn't exist.
    Should raise an InternalApiError.
    """

    inspection_id = "some_invalid_inspection_id"
    user_provided_key = "Operator"
    user_provided_value = "Bob"

    with pytest.raises(InternalApiError):
        gl.update_inspection_metadata(inspection_id, user_provided_key, user_provided_value)


def test_stop_inspection_pass(gl: Groundlight, detector: Detector):
    """Starts an inspection, submits a query with the inspection ID that should pass, stops
    the inspection, checks the result.
    """
    inspection_id = gl.start_inspection()

    _ = gl.submit_image_query(detector=detector, image="test/assets/dog.jpeg", inspection_id=inspection_id)

    assert gl.stop_inspection(inspection_id) == "PASS"


def test_stop_inspection_fail(gl: Groundlight, detector: Detector):
    """Starts an inspection, submits a query that should fail, stops
    the inspection, checks the result.
    """
    inspection_id = gl.start_inspection()

    iq = gl.submit_image_query(detector=detector, image="test/assets/cat.jpeg", inspection_id=inspection_id)
    gl.add_label(iq, Label.NO)  # labeling it NO just to be sure the inspection fails

    assert gl.stop_inspection(inspection_id) == "FAIL"


def test_stop_inspection_with_invalid_id(gl: Groundlight):
    inspection_id = "some_invalid_inspection_id"

    with pytest.raises(InternalApiError):
        gl.stop_inspection(inspection_id)


def test_update_detector_confidence_threshold_success(gl: Groundlight, detector: Detector):
    """Updates the confidence threshold for a detector. This should succeed."""
    gl.update_detector_confidence_threshold(detector.id, 0.77)


def test_update_detector_confidence_threshold_failure(gl: Groundlight, detector: Detector):
    """Attempts to update the confidence threshold for a detector to invalid values.
    Should raise ValueError exceptions.
    """
    with pytest.raises(ValueError):
        gl.update_detector_confidence_threshold(detector.id, 77)  # too high

    with pytest.raises(ValueError):
        gl.update_detector_confidence_threshold(detector.id, -1)  # too low
