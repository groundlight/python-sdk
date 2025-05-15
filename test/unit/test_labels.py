from datetime import datetime

import pytest
from groundlight import ApiException, ExperimentalApi


def test_binary_labels(gl_experimental: ExperimentalApi):
    name = f"Test binary labels{datetime.utcnow()}"
    det = gl_experimental.create_detector(name, "test_query")
    iq1 = gl_experimental.submit_image_query(det, "test/assets/cat.jpeg")
    gl_experimental.add_label(iq1, "YES")
    iq1 = gl_experimental.get_image_query(iq1.id)
    assert iq1.result.label == "YES"
    gl_experimental.add_label(iq1, "NO")
    iq1 = gl_experimental.get_image_query(iq1.id)
    assert iq1.result.label == "NO"
    gl_experimental.add_label(iq1, "UNCLEAR")
    iq1 = gl_experimental.get_image_query(iq1.id)
    assert iq1.result.label == "UNCLEAR"
    with pytest.raises(ApiException) as _:
        gl_experimental.add_label(iq1, "MAYBE")


def test_counting_labels(gl_experimental: ExperimentalApi):
    name = f"Test binary labels{datetime.utcnow()}"
    det = gl_experimental.create_counting_detector(name, "test_query", "test_object_class")
    iq1 = gl_experimental.submit_image_query(det, "test/assets/cat.jpeg")

    gl_experimental.add_label(iq1, 0)
    iq1 = gl_experimental.get_image_query(iq1.id)
    assert iq1.result.count == 0

    good_label = 5
    gl_experimental.add_label(iq1, good_label)
    iq1 = gl_experimental.get_image_query(iq1.id)
    assert iq1.result.count == good_label

    gl_experimental.add_label(iq1, "UNCLEAR")
    iq1 = gl_experimental.get_image_query(iq1.id)
    assert iq1.result.count is None

    with pytest.raises(ApiException) as _:
        gl_experimental.add_label(iq1, "MAYBE")
    with pytest.raises(ApiException) as _:
        gl_experimental.add_label(iq1, -999)


def test_multiclass_labels(gl_experimental: ExperimentalApi):
    name = f"Test binary labels{datetime.utcnow()}"
    det = gl_experimental.create_multiclass_detector(name, "test_query", class_names=["apple", "banana", "cherry"])
    iq1 = gl_experimental.submit_image_query(det, "test/assets/cat.jpeg")
    gl_experimental.add_label(iq1, "apple")
    iq1 = gl_experimental.get_image_query(iq1.id)
    assert iq1.result.label == "apple"
    gl_experimental.add_label(iq1, "banana")
    iq1 = gl_experimental.get_image_query(iq1.id)
    assert iq1.result.label == "banana"
    gl_experimental.add_label(iq1, "cherry")
    iq1 = gl_experimental.get_image_query(iq1.id)
    assert iq1.result.label == "cherry"
    # You can submit the index of the class as well
    gl_experimental.add_label(iq1, 2)
    iq1 = gl_experimental.get_image_query(iq1.id)
    assert iq1.result.label == "cherry"
    with pytest.raises(ApiException) as _:
        gl_experimental.add_label(iq1, "MAYBE")


def test_text_recognition_labels(gl_experimental: ExperimentalApi):
    name = f"Test text recognition labels{datetime.utcnow()}"
    det = gl_experimental.create_text_recognition_detector(name, "test_query")
    iq1 = gl_experimental.submit_image_query(det, "test/assets/cat.jpeg")
    gl_experimental.add_label(iq1, "apple text")
    iq1 = gl_experimental.get_image_query(iq1.id)
    assert iq1.result.text == "apple text"
    gl_experimental.add_label(iq1, "banana text")
    iq1 = gl_experimental.get_image_query(iq1.id)
    assert iq1.result.text == "banana text"
    gl_experimental.add_label(iq1, "")
    iq1 = gl_experimental.get_image_query(iq1.id)
    assert iq1.result.text == ""

    with pytest.raises(ApiException) as _:
        gl_experimental.add_label(iq1, "MAYBE")
