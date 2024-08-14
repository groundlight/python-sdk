from datetime import datetime

import pytest
from groundlight import ExperimentalApi
from model import ImageQuery


def test_detector_groups(gl_experimental: ExperimentalApi):
    """
    verify that we can create a detector group and retrieve it
    """
    name = f"Test {datetime.utcnow()}"
    created_group = gl_experimental.create_detector_group(name)
    all_groups = gl_experimental.list_detector_groups()
    assert created_group in all_groups


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