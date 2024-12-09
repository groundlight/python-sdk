from datetime import datetime

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
    updated_detector.escalation_type.value == "NO_HUMAN_LABELING"
    gl_experimental.update_detector_escalation_type(detector.id, "STANDARD")
    updated_detector = gl_experimental.get_detector(detector.id)
    updated_detector.escalation_type.value == "STANDARD"


@pytest.mark.skip(
    reason=(
        "Users currently don't have permission to turn object detection on their own. If you have questions, reach out"
        " to Groundlight support."
    )
)
def test_submit_roi(gl_experimental: ExperimentalApi, image_query_yes: ImageQuery):
    """
    verify that we can submit an ROI
    """
    label_name = "dog"
    roi = gl_experimental.create_roi(label_name, (0, 0), (0.5, 0.5))
    gl_experimental.add_label(image_query_yes.id, "YES", [roi])


@pytest.mark.skip(
    reason=(
        "Users currently don't have permission to turn object detection on their own. If you have questions, reach out"
        " to Groundlight support."
    )
)
def test_submit_multiple_rois(gl_experimental: ExperimentalApi, image_query_no: ImageQuery):
    """
    verify that we can submit multiple ROIs
    """
    label_name = "dog"
    roi = gl_experimental.create_roi(label_name, (0, 0), (0.5, 0.5))
    gl_experimental.add_label(image_query_no, "YES", [roi] * 3)


def test_counting_detector(gl_experimental: ExperimentalApi):
    """
    verify that we can create and submit to a counting detector
    """
    name = f"Test {datetime.utcnow()}"
    created_detector = gl_experimental.create_counting_detector(name, "How many dogs", "dog")
    assert created_detector is not None
    count_iq = gl_experimental.submit_image_query(created_detector, "test/assets/dog.jpeg")
    assert count_iq.result.count is not None


@pytest.mark.skip(
    reason=(
        "General users currently currently can't use multiclass detectors. If you have questions, reach out"
        " to Groundlight support, or upgrade your plan."
    )
)
def test_multiclass_detector(gl_experimental: ExperimentalApi):
    """
    verify that we can create and submit to a multi-class detector
    """
    name = f"Test {datetime.utcnow()}"
    class_names = ["Golden Retriever", "Labrador Retriever", "Poodle"]
    created_detector = gl_experimental.create_multiclass_detector(
        name, "What kind of dog is this?", class_names=class_names
    )
    assert created_detector is not None
    mc_iq = gl_experimental.submit_image_query(created_detector, "test/assets/dog.jpeg")
    assert mc_iq.result.label is not None
    assert mc_iq.result.label in class_names
