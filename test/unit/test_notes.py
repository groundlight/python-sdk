from datetime import datetime

from groundlight import ExperimentalApi


def test_notes(gl: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    det = gl.create_detector(name, "test_query")
    gl.create_note(det, "test_note")
    # test runner could be either a customer or GL
    notes = (gl.get_notes(det).get("customer") or []) + (gl.get_notes(det).get("gl") or [])
    found_note = False
    for i in range(len(notes)):
        if notes[i].content == "test_note":
            found_note = True
    assert found_note


def test_note_with_image(gl: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    det = gl.create_detector(name, "test_query")
    gl.create_note(det, "test_note", "test/assets/cat.jpeg")
    notes = (gl.get_notes(det).get("customer") or []) + (gl.get_notes(det).get("gl") or [])
    found_note = False
    for i in range(len(notes)):
        if notes[i].content == "test_note":
            found_note = True
            assert notes[i].image is not None
    assert found_note
