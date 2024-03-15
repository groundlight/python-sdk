from datetime import datetime, timezone

import pytest
from groundlight import ExperimentalApi


@pytest.fixture(name="gl")
def _gl() -> ExperimentalApi:
    return ExperimentalApi(endpoint="https://api.dev.groundlight.ai")


def test_notes(gl: ExperimentalApi):
    name = f"Test {datetime.now(timezone.utc)}"
    det = gl.create_detector(name, "test_query")
    gl.create_note(det, "test_note")
    notes = gl.get_notes(det)["customer"]
    found_note = False
    for i in range(len(notes)):
        if notes[i].content == "test_note":
            found_note = True
    assert found_note
