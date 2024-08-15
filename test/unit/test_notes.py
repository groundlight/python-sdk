from datetime import datetime

from groundlight import ExperimentalApi


def test_notes(gl_experimental: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    det = gl_experimental.create_detector(name, "test_query")
    gl_experimental.create_note(det, "test_note")
    # test runner could be either a customer or gl_experimental
    notes = (gl_experimental.get_notes(det).get("customer") or []) + (gl_experimental.get_notes(det).get("gl") or [])
    found_note = False
    for i in range(len(notes)):
        if notes[i].content == "test_note":
            found_note = True
    assert found_note


def test_note_with_image(gl_experimental: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    det = gl_experimental.create_detector(name, "test_query")
    gl_experimental.create_note(det, "test_note", "test/assets/cat.jpeg")
    notes = (gl_experimental.get_notes(det).get("customer") or []) + (gl_experimental.get_notes(det).get("gl") or [])
    found_note = False
    for i in range(len(notes)):
        if notes[i].content == "test_note":
            found_note = True
    assert found_note
