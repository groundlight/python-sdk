from datetime import datetime

import pytest
from groundlight import ExperimentalApi
from openapi_client.exceptions import ApiAttributeError


@pytest.fixture(name="gl")
def _gl() -> ExperimentalApi:
    return ExperimentalApi()


def test_notes(gl: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    det = gl.create_detector(name, "test_query")
    gl.create_note(det, "test_note")
    # test runner could be either a customer or GL
    try:
        notes = gl.get_notes(det)["GL"]
        found_note = False
        for i in range(len(notes)):
            if notes[i].content == "test_note":
                found_note = True
        assert found_note
    except (AssertionError, ApiAttributeError):
        notes = gl.get_notes(det)["customer"]
        found_note = False
        for i in range(len(notes)):
            if notes[i].content == "test_note":
                found_note = True
        assert found_note
