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
    gl_experimental.update_detector_confidence_threshold(detector.id, 0.5)
    updated_detector = gl_experimental.get_detector(detector.id)
    assert updated_detector.confidence_threshold == 0.5
    gl_experimental.update_detector_confidence_threshold(detector.id, 0.9)
    updated_detector = gl_experimental.get_detector(detector.id)
    assert updated_detector.confidence_threshold == 0.9


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
