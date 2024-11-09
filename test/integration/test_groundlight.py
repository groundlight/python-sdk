# Optional star-imports are weird and not usually recommended ...
# ruff: noqa: F403,F405
# pylint: disable=wildcard-import,unused-wildcard-import,redefined-outer-name,import-outside-toplevel
import json
import random
import string
import time
from datetime import datetime
from typing import Any, Dict, Optional, Union

import pytest
from groundlight import Groundlight
from groundlight.binary_labels import VALID_DISPLAY_LABELS, DeprecatedLabel, Label, convert_internal_label_to_display
from groundlight.internalapi import ApiException, InternalApiError, NotFoundError
from groundlight.optional_imports import *
from groundlight.status_codes import is_user_error
from ksuid import KsuidMs
from model import (
    BinaryClassificationResult,
    CountingResult,
    Detector,
    ImageQuery,
    PaginatedDetectorList,
    PaginatedImageQueryList,
)

DEFAULT_CONFIDENCE_THRESHOLD = 0.9
IQ_IMPROVEMENT_THRESHOLD = 0.75


def is_valid_display_result(result: Any) -> bool:
    """Is the image query result valid to display to the user?."""
    if not isinstance(result, BinaryClassificationResult) and not isinstance(result, CountingResult):
        return False
    if not is_valid_display_label(result.label):
        return False
    return True


def generate_random_dict(target_size_bytes=1024, key_length=8, value_length=10) -> Dict[str, str]:
    """
    Generate a random dictionary with an approximate size in bytes.
    """
    key_chars = string.ascii_lowercase + string.digits
    value_chars = string.ascii_letters + string.digits

    random_dict: Dict[str, str] = {}
    while len(json.dumps(random_dict).encode("utf-8")) < target_size_bytes:
        key = "".join(random.choice(key_chars) for _ in range(key_length))
        value = "".join(random.choice(value_chars) for _ in range(value_length))
        random_dict[key] = value

        # Check if adding another pair would likely exceed the size
        # The 4 is for the quotes around the key and value, and the colon and comma
        if len(json.dumps(random_dict).encode("utf-8")) + key_length + value_length + 4 > target_size_bytes:
            break

    return random_dict


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
    iq = gl.submit_image_query(detector=detector.id, image="test/assets/dog.jpeg", human_review="NEVER")
    return iq


@pytest.fixture(name="image_query_no")
def fixture_image_query_no(gl: Groundlight, detector: Detector) -> ImageQuery:
    iq = gl.submit_image_query(detector=detector.id, image="test/assets/cat.jpeg", human_review="NEVER")
    return iq


@pytest.fixture(name="image")
def fixture_image() -> str:
    return "test/assets/dog.jpeg"


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

    # If you retrieve an existing detector, we currently require the group_name, confidence, query to match
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

    different_group_name = "Different group"
    with pytest.raises(ValueError):
        gl.get_or_create_detector(
            name=name,
            query=query,
            confidence_threshold=confidence_threshold,
            pipeline_config=pipeline_config,
            group_name=different_group_name,
        )

    # If the confidence is not provided, we will use the existing detector's confidence.
    retrieved_detector = gl.get_or_create_detector(name=name, query=query)
    assert (
        retrieved_detector.confidence_threshold == confidence_threshold
    ), "We expected to retrieve the existing detector's confidence, but got a different value."


@pytest.mark.skip_for_edge_endpoint(reason="The edge-endpoint does not support passing detector metadata.")
def test_create_detector_with_everything(gl: Groundlight):
    name = f"Test {datetime.utcnow()}"  # Need a unique name
    query = "Is there a dog?"
    group_name = "Test group"
    confidence_threshold = 0.825
    patience_time = 300  # seconds
    pipeline_config = "never-review"
    metadata = generate_random_dict(target_size_bytes=200)
    detector = gl.create_detector(
        name=name,
        query=query,
        group_name=group_name,
        confidence_threshold=confidence_threshold,
        patience_time=patience_time,
        pipeline_config=pipeline_config,
        metadata=metadata,
    )
    assert isinstance(detector, Detector)
    assert detector.name == name
    assert detector.query == query
    assert detector.group_name == group_name
    assert detector.confidence_threshold == confidence_threshold
    # TODO: We need a backend update to get the serialized output
    # assert detector.patience_time == patience_time
    # GL runs multiple models synchronously, and the active pipeline may change.
    # Currently, we don't check the pipeline config here.
    assert detector.metadata == metadata


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


def test_ask_confident(gl: Groundlight, detector: Detector):
    _image_query = gl.ask_confident(detector=detector.id, image="test/assets/dog.jpeg", wait=10)
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)
    assert is_valid_display_result(_image_query.result)


def test_ask_ml(gl: Groundlight, detector: Detector):
    _image_query = gl.ask_ml(detector=detector.id, image="test/assets/dog.jpeg", wait=10)
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)
    assert is_valid_display_result(_image_query.result)


def test_submit_image_query(gl: Groundlight, detector: Detector):
    def validate_image_query(_image_query: ImageQuery):
        assert str(_image_query)
        assert isinstance(_image_query, ImageQuery)
        assert is_valid_display_result(_image_query.result)

    _image_query = gl.submit_image_query(
        detector=detector.id, image="test/assets/dog.jpeg", wait=10, human_review="NEVER"
    )
    validate_image_query(_image_query)
    _image_query = gl.submit_image_query(
        detector=detector.id, image="test/assets/dog.jpeg", wait=3, human_review="NEVER"
    )
    validate_image_query(_image_query)
    _image_query = gl.submit_image_query(
        detector=detector.id, image="test/assets/dog.jpeg", wait=10, patience_time=20, human_review="NEVER"
    )
    validate_image_query(_image_query)
    _image_query = gl.submit_image_query(detector=detector.id, image="test/assets/dog.jpeg", human_review="NEVER")
    validate_image_query(_image_query)
    _image_query = gl.submit_image_query(
        detector=detector.id, image="test/assets/dog.jpeg", wait=180, confidence_threshold=0.75, human_review="NEVER"
    )
    validate_image_query(_image_query)
    assert _image_query.result.confidence >= IQ_IMPROVEMENT_THRESHOLD


def test_submit_image_query_blocking(gl: Groundlight, detector: Detector):
    _image_query = gl.submit_image_query(
        detector=detector.id, image="test/assets/dog.jpeg", wait=10, human_review="NEVER"
    )
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)
    assert is_valid_display_result(_image_query.result)


def test_submit_image_query_returns_yes(gl: Groundlight):
    # We use the "never-review" pipeline to guarantee a confident "yes" answer.
    detector = gl.get_or_create_detector(name="Always a dog", query="Is there a dog?", pipeline_config="never-review")
    image_query = gl.submit_image_query(detector=detector, image="test/assets/dog.jpeg", wait=10, human_review="NEVER")
    assert image_query.result.label == Label.YES


def test_submit_image_query_returns_text(gl: Groundlight):
    # We use the "never-review" pipeline to guarantee a confident "yes" answer.
    detector = gl.get_or_create_detector(
        name="Always same text", query="Is there a dog?", pipeline_config="constant-text"
    )
    image_query = gl.submit_image_query(detector=detector, image="test/assets/dog.jpeg", wait=10, human_review="NEVER")
    assert isinstance(image_query.text, str)


def test_submit_image_query_filename(gl: Groundlight, detector: Detector):
    _image_query = gl.submit_image_query(detector=detector.id, image="test/assets/dog.jpeg", human_review="NEVER")
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)
    assert is_valid_display_result(_image_query.result)


def test_submit_image_query_png(gl: Groundlight, detector: Detector):
    _image_query = gl.submit_image_query(detector=detector.id, image="test/assets/cat.png", human_review="NEVER")
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)
    assert is_valid_display_result(_image_query.result)


def test_submit_image_query_with_id(gl: Groundlight, detector: Detector):
    # submit_image_query
    id = f"iq_{KsuidMs()}"
    _image_query = gl.submit_image_query(
        detector=detector.id, image="test/assets/dog.jpeg", wait=10, human_review="NEVER", image_query_id=id
    )
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)
    assert is_valid_display_result(_image_query.result)
    assert _image_query.metadata is not None
    assert _image_query.metadata.get("is_from_edge")

    # ask_confident
    id = f"iq_{KsuidMs()}"
    _image_query = gl.ask_confident(detector=detector.id, image="test/assets/dog.jpeg", wait=10, image_query_id=id)

    # ask_ml
    id = f"iq_{KsuidMs()}"
    _image_query = gl.ask_ml(detector=detector.id, image="test/assets/dog.jpeg", wait=10, image_query_id=id)

    # ask_async
    id = f"iq_{KsuidMs()}"
    _image_query = gl.ask_async(detector=detector.id, image="test/assets/dog.jpeg", image_query_id=id)


def test_submit_image_query_with_invalid_id(gl: Groundlight, detector: Detector):
    # Invalid ID format
    id = f"iqabc_{KsuidMs()}"
    with pytest.raises(ApiException):
        gl.submit_image_query(
            detector=detector.id, image="test/assets/dog.jpeg", wait=10, human_review="NEVER", image_query_id=id
        )

    # Duplicate ID entry
    id = f"iq_{KsuidMs()}"
    _image_query_1 = gl.submit_image_query(
        detector=detector.id, image="test/assets/dog.jpeg", wait=10, human_review="NEVER", image_query_id=id
    )
    assert str(_image_query_1)
    assert isinstance(_image_query_1, ImageQuery)
    assert is_valid_display_result(_image_query_1.result)
    with pytest.raises(ApiException):
        gl.submit_image_query(
            detector=detector.id, image="test/assets/dog.jpeg", wait=10, human_review="NEVER", image_query_id=id
        )


def test_submit_image_query_with_human_review_param(gl: Groundlight, detector: Detector):
    # For now, this just tests that the image query is submitted successfully.
    # There should probably be a better way to check whether the image query was escalated for human review.

    for human_review_value in ("DEFAULT", "ALWAYS", "NEVER"):
        _image_query = gl.submit_image_query(
            detector=detector.id, image="test/assets/dog.jpeg", human_review=human_review_value
        )
        assert is_valid_display_result(_image_query.result)


@pytest.mark.skip_for_edge_endpoint(reason="The edge-endpoint does not support passing detector metadata.")
def test_create_detector_with_metadata(gl: Groundlight):
    name = f"Test {datetime.utcnow()}"  # Need a unique name
    query = "Is there a dog?"
    metadata = generate_random_dict(target_size_bytes=200)
    detector = gl.create_detector(name=name, query=query, metadata=metadata)
    assert detector.metadata == metadata

    retrieved_detector = gl.get_detector(id=detector.id)
    assert retrieved_detector.metadata == metadata


@pytest.mark.skip_for_edge_endpoint(reason="The edge-endpoint does not support passing detector metadata.")
def test_get_or_create_detector_with_metadata(gl: Groundlight):
    unique_name = f"Unique name {datetime.utcnow()}"
    query = "Is there a dog?"
    metadata = generate_random_dict(target_size_bytes=200)
    detector = gl.get_or_create_detector(name=unique_name, query=query, metadata=metadata)
    assert detector.metadata == metadata

    retrieved_detector = gl.get_or_create_detector(name=unique_name, query=query, metadata=metadata)
    assert retrieved_detector.id == detector.id
    assert retrieved_detector.metadata == metadata


@pytest.mark.skip_for_edge_endpoint(reason="The edge-endpoint does not support passing detector metadata.")
@pytest.mark.parametrize(
    "metadata_list",
    [
        [generate_random_dict(target_size_bytes=3000)],
        ["this is not valid JSON"],
        [""],
    ],
)
def test_create_detector_with_invalid_metadata(gl: Groundlight, metadata_list: Any):
    name = f"Test {datetime.utcnow()}"  # Need a unique name
    query = "Is there a dog?"

    for metadata in metadata_list:
        with pytest.raises((TypeError, ValueError)):
            gl.create_detector(name=name, query=query, metadata=metadata)


@pytest.mark.skip_for_edge_endpoint(reason="The edge-endpoint does not support passing image query metadata.")
@pytest.mark.parametrize("metadata", [None, {}, {"a": 1}, '{"a": 1}'])
def test_submit_image_query_with_metadata(
    gl: Groundlight, detector: Detector, image: str, metadata: Union[Dict, str, None]
):
    # We expect the returned value to be a dict
    expected_metadata: Optional[Dict] = json.loads(metadata) if isinstance(metadata, str) else metadata

    iq = gl.submit_image_query(detector=detector.id, image=image, human_review="NEVER", metadata=metadata)
    assert iq.metadata == expected_metadata

    # Test that we can retrieve the metadata from the server at a later time
    retrieved_iq = gl.get_image_query(id=iq.id)
    assert retrieved_iq.metadata == expected_metadata


@pytest.mark.skip_for_edge_endpoint(reason="The edge-endpoint does not support passing metadata.")
def test_ask_methods_with_metadata(gl: Groundlight, detector: Detector, image: str):
    metadata = {"a": 1}
    iq = gl.ask_ml(detector=detector.id, image=image, metadata=metadata)
    assert iq.metadata == metadata

    iq = gl.ask_async(detector=detector.id, image=image, human_review="NEVER", metadata=metadata)
    assert iq.metadata == metadata

    # `ask_confident()` can make our unit tests take longer, so we don't include it here.
    # iq = gl.ask_confident(detector=detector.id, image=image, metadata=metadata)
    # assert iq.metadata == metadata


@pytest.mark.skip_for_edge_endpoint(reason="The edge-endpoint does not support passing metadata.")
@pytest.mark.parametrize("metadata", ["", "a", b'{"a": 1}'])
def test_submit_image_query_with_invalid_metadata(gl: Groundlight, detector: Detector, image: str, metadata: Any):
    with pytest.raises(TypeError):
        gl.submit_image_query(detector=detector.id, image=image, human_review="NEVER", metadata=metadata)


@pytest.mark.skip_for_edge_endpoint(reason="The edge-endpoint does not support passing metadata.")
def test_submit_image_query_with_metadata_too_large(gl: Groundlight, detector: Detector, image: str):
    with pytest.raises(ValueError):
        gl.submit_image_query(
            detector=detector.id,
            image=image,
            human_review="NEVER",
            metadata={"a": "b" * 2000},  # More than 1KB
        )


@pytest.mark.run_only_for_edge_endpoint
def test_submit_image_query_with_metadata_returns_user_error(gl: Groundlight, detector: Detector, image: str):
    """On the edge-endpoint, we raise an exception if the user passes metadata."""
    with pytest.raises(ApiException) as exc_info:
        gl.submit_image_query(detector=detector.id, image=image, human_review="NEVER", metadata={"a": 1})
    assert is_user_error(exc_info.value.status)


def test_submit_image_query_jpeg_bytes(gl: Groundlight, detector: Detector):
    jpeg = open("test/assets/dog.jpeg", "rb").read()
    _image_query = gl.submit_image_query(detector=detector.id, image=jpeg, human_review="NEVER")
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)
    assert is_valid_display_result(_image_query.result)


def test_submit_image_query_jpeg_truncated(gl: Groundlight, detector: Detector):
    jpeg = open("test/assets/dog.jpeg", "rb").read()
    jpeg_truncated = jpeg[:-500]  # Cut off the last 500 bytes
    # This is an extra difficult test because the header is valid.
    # So a casual check of the image will appear valid.
    with pytest.raises(ApiException) as exc_info:
        _image_query = gl.submit_image_query(detector=detector.id, image=jpeg_truncated, human_review="NEVER")
    exc_value = exc_info.value
    assert is_user_error(exc_value.status)


def test_submit_image_query_bad_filename(gl: Groundlight, detector: Detector):
    with pytest.raises(FileNotFoundError):
        _image_query = gl.submit_image_query(detector=detector.id, image="missing-file.jpeg", human_review="NEVER")


def test_submit_image_query_bad_jpeg_file(gl: Groundlight, detector: Detector):
    with pytest.raises(ValueError) as exc_info:
        _image_query = gl.submit_image_query(
            detector=detector.id, image="test/assets/blankfile.jpeg", human_review="NEVER"
        )
    assert "jpeg" in str(exc_info).lower()


@pytest.mark.skipif(MISSING_PIL, reason="Needs pillow")  # type: ignore
def test_submit_image_query_pil(gl: Groundlight, detector: Detector):
    # generates a pil image and submits it
    from PIL import Image

    dog = Image.open("test/assets/dog.jpeg")
    _image_query = gl.submit_image_query(detector=detector.id, image=dog, human_review="NEVER")

    black = Image.new("RGB", (640, 480))
    _image_query = gl.submit_image_query(detector=detector.id, image=black, human_review="NEVER")


def test_submit_image_query_wait_and_want_async_causes_exception(gl: Groundlight, detector: Detector):
    """
    Tests that attempting to use the wait and want_async parameters together causes an exception.
    """

    with pytest.raises(ValueError):
        _image_query = gl.submit_image_query(
            detector=detector.id, image="test/assets/dog.jpeg", wait=10, want_async=True, human_review="NEVER"
        )


def test_submit_image_query_with_want_async_workflow(gl: Groundlight, detector: Detector):
    """
    Tests the workflow for submitting an image query with the want_async parameter set to True.
    """

    _image_query = gl.submit_image_query(
        detector=detector.id, image="test/assets/dog.jpeg", wait=0, want_async=True, human_review="NEVER"
    )

    # the result should be None
    assert _image_query.result is None

    # attempting to access fields within the result should raise an exception
    with pytest.raises(AttributeError):
        _ = _image_query.result.label  # type: ignore
    with pytest.raises(AttributeError):
        _ = _image_query.result.confidence  # type: ignore
    time.sleep(5)
    # you should be able to get a "real" result by retrieving an updated image query object from the server
    _image_query = gl.get_image_query(id=_image_query.id)
    assert _image_query.result is not None
    assert _image_query.result.label in VALID_DISPLAY_LABELS


def test_ask_async_workflow(gl: Groundlight, detector: Detector):
    """
    Tests the workflow for submitting an image query with ask_async.
    """
    _image_query = gl.ask_async(detector=detector.id, image="test/assets/dog.jpeg")

    # the result should be None
    assert _image_query.result is None

    # attempting to access fields within the result should raise an exception
    with pytest.raises(AttributeError):
        _ = _image_query.result.label  # type: ignore
    with pytest.raises(AttributeError):
        _ = _image_query.result.confidence  # type: ignore

    time.sleep(5)

    # you should be able to get a "real" result by retrieving an updated image query object from the server
    _image_query = gl.get_image_query(id=_image_query.id)
    assert _image_query.result is not None
    assert _image_query.result.label in VALID_DISPLAY_LABELS


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


def test_get_image_query_label_yes(gl: Groundlight, image_query_yes: ImageQuery):
    gl.add_label(image_query_yes, Label.YES)
    retrieved_iq = gl.get_image_query(id=image_query_yes.id)
    assert retrieved_iq.result.label == Label.YES


def test_get_image_query_label_no(gl: Groundlight, image_query_no: ImageQuery):
    gl.add_label(image_query_no, Label.NO)
    retrieved_iq = gl.get_image_query(id=image_query_no.id)
    assert retrieved_iq.result.label == Label.NO


def test_add_label_to_object(gl: Groundlight, image_query_yes: ImageQuery):
    assert isinstance(image_query_yes, ImageQuery)
    gl.add_label(image_query_yes, Label.YES)


def test_add_label_by_id(gl: Groundlight, image_query_no: ImageQuery):
    iqid = image_query_no.id
    # TODO: Fully deprecate chk_ prefix
    assert iqid.startswith(("chk_", "iq_"))
    gl.add_label(iqid, Label.NO)


def test_add_label_names(gl: Groundlight, image_query_yes: ImageQuery, image_query_no: ImageQuery):
    iqid_yes = image_query_yes.id
    iqid_no = image_query_no.id

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
        gl.add_label(iqid_yes, Label.UNCLEAR)


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
    _image_query = gl.submit_image_query(detector=detector.id, image=np_img, human_review="NEVER")
    assert str(_image_query)
    assert isinstance(_image_query, ImageQuery)
    assert is_valid_display_result(_image_query.result)


@pytest.mark.skip_for_edge_endpoint(reason="The edge-endpoint doesn't support inspection_id")
def test_start_inspection(gl: Groundlight):
    inspection_id = gl.start_inspection()

    assert isinstance(inspection_id, str)
    assert "inspect_" in inspection_id


@pytest.mark.skip_for_edge_endpoint(reason="The edge-endpoint doesn't support inspection_id")
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


@pytest.mark.skip_for_edge_endpoint(reason="The edge-endpoint doesn't support inspection_id")
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


@pytest.mark.skip_for_edge_endpoint(reason="The edge-endpoint doesn't support inspection_id")
def test_update_inspection_metadata_invalid_inspection_id(gl: Groundlight):
    """Attempt to update metadata for an inspection that doesn't exist.
    Should raise an InternalApiError.
    """

    inspection_id = "some_invalid_inspection_id"
    user_provided_key = "Operator"
    user_provided_value = "Bob"

    with pytest.raises(InternalApiError):
        gl.update_inspection_metadata(inspection_id, user_provided_key, user_provided_value)


@pytest.mark.skip_for_edge_endpoint(reason="The edge-endpoint doesn't support inspection_id")
def test_stop_inspection_pass(gl: Groundlight, detector: Detector):
    """Starts an inspection, submits a query with the inspection ID that should pass, stops
    the inspection, checks the result.
    """
    inspection_id = gl.start_inspection()

    _ = gl.submit_image_query(detector=detector, image="test/assets/dog.jpeg", inspection_id=inspection_id)

    assert gl.stop_inspection(inspection_id) == "PASS"


@pytest.mark.skip_for_edge_endpoint(reason="The edge-endpoint doesn't support inspection_id")
def test_stop_inspection_fail(gl: Groundlight, detector: Detector):
    """Starts an inspection, submits a query that should fail, stops
    the inspection, checks the result.
    """
    inspection_id = gl.start_inspection()

    iq = gl.submit_image_query(detector=detector, image="test/assets/cat.jpeg", inspection_id=inspection_id)
    gl.add_label(iq, Label.NO)  # labeling it NO just to be sure the inspection fails

    assert gl.stop_inspection(inspection_id) == "FAIL"


@pytest.mark.skip_for_edge_endpoint(reason="The edge-endpoint doesn't support inspection_id")
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


@pytest.mark.skip_for_edge_endpoint(reason="The edge-endpoint does not support passing detector metadata.")
def test_submit_image_query_with_inspection_id_metadata_and_want_async(gl: Groundlight, detector: Detector, image: str):
    inspection_id = gl.start_inspection()
    metadata = {"key": "value"}
    iq = gl.submit_image_query(
        detector=detector.id,
        image=image,
        human_review="NEVER",
        inspection_id=inspection_id,
        metadata=metadata,
        want_async=True,
        wait=0,
    )

    iq = gl.get_image_query(iq.id)
    iq = gl.wait_for_confident_result(iq.id)

    assert iq.metadata == metadata
    assert iq.result.label == Label.YES


def test_submit_image_query_with_empty_inspection_id(gl: Groundlight, detector: Detector, image: str):
    """The URCap submits the inspection_id as an empty string when there is no active inspection.
    This test ensures that this behavior is allowed and does not raise an exception.
    """
    gl.submit_image_query(
        detector=detector.id,
        image=image,
        human_review="NEVER",
        inspection_id="",
    )
