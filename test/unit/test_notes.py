import pytest
from groundlight import ExperimentalApi


@pytest.fixture(name="gl")
def _gl() -> ExperimentalApi:
    return ExperimentalApi(endpoint="https://api.dev.groundlight.ai")


def test_notes(gl: ExperimentalApi):
    det = gl.get_or_create_detector("test_detector", "test_query")
    gl.create_note(det, "test_note")
    note = gl.get_notes(det)
    assert note.message == "test_note"
