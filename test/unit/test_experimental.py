from datetime import datetime

from groundlight import ExperimentalApi


def test_detector_groups(gl: ExperimentalApi):
    """
    verify that we can create a detector group and retrieve it
    """
    name = f"Test {datetime.utcnow()}"
    created_group = gl.create_detector_group(name)
    all_groups = gl.list_detector_groups()
    assert created_group in all_groups
