from datetime import datetime

import pytest
from groundlight import ExperimentalApi
from groundlight_openapi_client.exceptions import NotFoundException


def test_detector_groups(gl: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    created_group = gl.create_detector_group(name)
    all_groups = gl.list_detector_groups()
    assert created_group in all_groups
