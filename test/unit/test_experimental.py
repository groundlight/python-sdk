import time
from datetime import datetime, timezone

import pytest
from groundlight import ExperimentalApi
from model import Detector, ImageQuery


def test_detector_groups(gl_experimental: ExperimentalApi):
    """
    verify that we can create a detector group and retrieve it
    """
    name = f"Test {datetime.utcnow()}"
    created_group = gl_experimental.create_detector_group(name)
    all_groups = gl_experimental.list_detector_groups()
    assert created_group in all_groups


def test_update_detector_confidence_threshold(gl_experimental: ExperimentalApi, detector: Detector):
    """
    verify that we can update the confidence of a detector
    """
    new_confidence = 0.5
    gl_experimental.update_detector_confidence_threshold(detector.id, new_confidence)
    updated_detector = gl_experimental.get_detector(detector.id)
    assert updated_detector.confidence_threshold == new_confidence
    newer_confidence = 0.9
    gl_experimental.update_detector_confidence_threshold(detector.id, newer_confidence)
    updated_detector = gl_experimental.get_detector(detector.id)
    assert updated_detector.confidence_threshold == newer_confidence


def test_update_detector_name(gl_experimental: ExperimentalApi, detector: Detector):
    """
    verify that we can update the name of a detector
    """
    new_name = f"Test {datetime.utcnow()}"
    gl_experimental.update_detector_name(detector.id, new_name)
    updated_detector = gl_experimental.get_detector(detector.id)
    assert updated_detector.name == new_name


def test_update_detector_status(gl_experimental: ExperimentalApi):
    """
    verify that we can update the status of a detector
    """
    detector = gl_experimental.get_or_create_detector(f"test {datetime.utcnow()}", "Is there a dog?")
    gl_experimental.update_detector_status(detector.id, False)
    updated_detector = gl_experimental.get_detector(detector.id)
    assert updated_detector.status.value == "OFF"
    gl_experimental.update_detector_status(detector.id, True)
    updated_detector = gl_experimental.get_detector(detector.id)
    assert updated_detector.status.value == "ON"


def test_update_detector_escalation_type(gl_experimental: ExperimentalApi):
    """
    verify that we can update the escalation type of a detector
    """
    detector = gl_experimental.get_or_create_detector(f"test {datetime.utcnow()}", "Is there a dog?")
    gl_experimental.update_detector_escalation_type(detector.id, "NO_HUMAN_LABELING")
    updated_detector = gl_experimental.get_detector(detector.id)
    updated_detector.escalation_type == "NO_HUMAN_LABELING"
    gl_experimental.update_detector_escalation_type(detector.id, "STANDARD")
    updated_detector = gl_experimental.get_detector(detector.id)
    updated_detector.escalation_type == "STANDARD"


def test_submit_roi(gl_experimental: ExperimentalApi, image_query_one: ImageQuery):
    """
    verify that we can submit an ROI
    """
    label_name = "dog"
    roi = gl_experimental.create_roi(label_name, (0, 0), (0.5, 0.5))
    gl_experimental.add_label(image_query_one.id, "YES", [roi])


@pytest.mark.skip(
    reason=(
        "Users currently don't have permission to turn object detection on their own. If you have questions, reach out"
        " to Groundlight support."
    )
)
def test_submit_multiple_rois(gl_experimental: ExperimentalApi, image_query_one: ImageQuery):
    """
    verify that we can submit multiple ROIs
    """
    label_name = "dog"
    roi = gl_experimental.create_roi(label_name, (0, 0), (0.5, 0.5))
    gl_experimental.add_label(image_query_one, 3, [roi] * 3)


def test_counting_detector(gl_experimental: ExperimentalApi):
    """
    verify that we can create and submit to a counting detector
    """
    name = f"Test {datetime.utcnow()}"
    created_detector = gl_experimental.create_counting_detector(name, "How many dogs", "dog", confidence_threshold=0.0)
    assert created_detector is not None
    count_iq = gl_experimental.submit_image_query(created_detector, "test/assets/dog.jpeg")
    assert count_iq.result.count is not None


def test_counting_detector_async(gl_experimental: ExperimentalApi):
    """
    verify that we can create and submit to a counting detector
    """
    name = f"Test {datetime.utcnow()}"
    created_detector = gl_experimental.create_counting_detector(name, "How many dogs", "dog", confidence_threshold=0.0)
    assert created_detector is not None
    async_iq = gl_experimental.ask_async(created_detector, "test/assets/dog.jpeg")
    # attempting to access fields within the result should raise an exception
    with pytest.raises(AttributeError):
        _ = async_iq.result.label  # type: ignore
    with pytest.raises(AttributeError):
        _ = async_iq.result.confidence  # type: ignore
    time.sleep(5)
    # you should be able to get a "real" result by retrieving an updated image query object from the server
    _image_query = gl_experimental.get_image_query(id=async_iq.id)
    assert _image_query.result is not None


def test_multiclass_detector(gl_experimental: ExperimentalApi):
    """
    verify that we can create and submit to a multi-class detector
    """
    name = f"Test {datetime.utcnow()}"
    class_names = ["Golden Retriever", "Labrador Retriever", "Poodle"]
    created_detector = gl_experimental.create_multiclass_detector(
        name, "What kind of dog is this?", class_names=class_names, confidence_threshold=0.0
    )
    assert created_detector is not None
    mc_iq = gl_experimental.submit_image_query(created_detector, "test/assets/dog.jpeg")
    assert mc_iq.result.label is not None
    assert mc_iq.result.label in class_names


def test_text_recognition_detector(gl_experimental: ExperimentalApi):
    """
    verify that we can create and submit to a text recognition detector
    """
    name = f"Test {datetime.utcnow()}"
    created_detector = gl_experimental.create_text_recognition_detector(
        name, "What is the date and time?", confidence_threshold=0.0
    )
    assert created_detector is not None
    mc_iq = gl_experimental.submit_image_query(created_detector, "test/assets/dog.jpeg")
    assert mc_iq.result.text is not None


@pytest.mark.skip(
    reason=(
        "General users currently currently can't use bounding box detectors. If you have questions, reach out"
        " to Groundlight support, or upgrade your plan."
    )
)
def test_bounding_box_detector(gl_experimental: ExperimentalApi):
    """
    Verify that we can create and submit to a bounding box detector
    """
    name = f"Test {datetime.now(timezone.utc)}"
    created_detector = gl_experimental.create_bounding_box_detector(
        name, "Draw a bounding box around each dog in the image", "dog", confidence_threshold=0.0
    )
    assert created_detector is not None
    bbox_iq = gl_experimental.submit_image_query(created_detector, "test/assets/dog.jpeg")
    assert bbox_iq.result.label is not None
    assert bbox_iq.rois is not None


@pytest.mark.skip(
    reason=(
        "General users currently currently can't use bounding box detectors. If you have questions, reach out"
        " to Groundlight support, or upgrade your plan."
    )
)
def test_bounding_box_detector_async(gl_experimental: ExperimentalApi):
    """
    Verify that we can create and submit to a bounding box detector with ask_async
    """
    name = f"Test {datetime.now(timezone.utc)}"
    created_detector = gl_experimental.create_bounding_box_detector(
        name, "Draw a bounding box around each dog in the image", "dog", confidence_threshold=0.0
    )
    assert created_detector is not None
    async_iq = gl_experimental.ask_async(created_detector, "test/assets/dog.jpeg")

    # attempting to access fields within the result should raise an exception
    with pytest.raises(AttributeError):
        _ = async_iq.result.label  # type: ignore
    with pytest.raises(AttributeError):
        _ = async_iq.result.confidence  # type: ignore

    time.sleep(5)
    # you should be able to get a "real" result by retrieving an updated image query object from the server
    _image_query = gl_experimental.get_image_query(id=async_iq.id)
    assert _image_query.result is not None
