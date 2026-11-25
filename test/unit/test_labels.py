from http import HTTPStatus
from typing import Callable
from unittest import mock

import pytest
from groundlight import ApiException, ExperimentalApi

from test.retry_decorator import retry_on_failure

EDGE_CONFIDENCE = 0.8


@retry_on_failure()
def test_binary_labels(gl_experimental: ExperimentalApi, detector_name: Callable):
    det = gl_experimental.create_detector(detector_name("Test binary labels"), "test_query")
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


@retry_on_failure()
def test_counting_labels(gl_experimental: ExperimentalApi, detector_name: Callable):
    det = gl_experimental.create_counting_detector(
        detector_name("Test counting labels"), "test_query", "test_object_class"
    )
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


@retry_on_failure()
def test_multiclass_labels(gl_experimental: ExperimentalApi, detector_name: Callable):
    det = gl_experimental.create_multiclass_detector(
        detector_name("Test multiclass labels"), "test_query", class_names=["apple", "banana", "cherry"]
    )
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


@retry_on_failure()
def test_bounding_box_labels(gl_experimental: ExperimentalApi, detector_name: Callable):
    det = gl_experimental.create_bounding_box_detector(
        detector_name("Test bounding box labels"), "test_query", "test_class"
    )
    iq1 = gl_experimental.submit_image_query(det, "test/assets/cat.jpeg")
    gl_experimental.add_label(iq1, "NO_OBJECTS")
    iq1 = gl_experimental.get_image_query(iq1.id)
    assert iq1.result.label == "NO_OBJECTS"
    gl_experimental.add_label(
        iq1,
        "BOUNDING_BOX",
        rois=[gl_experimental.create_roi(label="test_class", top_left=(0.1, 0.1), bottom_right=(0.6, 0.6))],
    )
    iq1 = gl_experimental.get_image_query(iq1.id)
    assert iq1.result.label == "BOUNDING_BOX"
    with pytest.raises(ApiException) as _:
        gl_experimental.add_label(iq1, "MAYBE")


@retry_on_failure()
def test_text_recognition_labels(gl_experimental: ExperimentalApi, detector_name: Callable):
    det = gl_experimental.create_text_recognition_detector(detector_name("Test text recognition labels"), "test_query")
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

    gl_experimental.add_label(iq1, "UNCLEAR")
    iq1 = gl_experimental.get_image_query(iq1.id)
    assert iq1.result.text is None


def test_add_edge_label_sends_edge_fields(gl_experimental: ExperimentalApi):
    roi = gl_experimental.create_roi(label="test_class", top_left=(0.1, 0.1), bottom_right=(0.6, 0.6))
    roi.score = 0.7
    with mock.patch.object(gl_experimental.labels_api, "create_label") as create_label:
        gl_experimental.add_edge_label("iq_abc", 1, confidence=EDGE_CONFIDENCE, model_binary_id="edge-key", rois=[roi])
        gl_experimental.add_edge_label("iq_abc", 0, confidence=EDGE_CONFIDENCE, model_binary_id="edge-key", rois=[])

    with_rois, without_rois = (call.args[0] for call in create_label.call_args_list)
    assert with_rois.from_edge is True
    assert with_rois.label == "1"
    assert with_rois.confidence == EDGE_CONFIDENCE
    assert with_rois.model_binary_id == "edge-key"
    assert [r.score for r in with_rois.rois] == [0.7]
    assert without_rois.rois == []


@retry_on_failure()
def test_edge_label_allows_one_per_image_query(gl_experimental: ExperimentalApi, detector_name: Callable):
    det = gl_experimental.create_detector(detector_name("Test edge labels"), "test_query")
    iq = gl_experimental.submit_image_query(det, "test/assets/cat.jpeg")

    gl_experimental.add_edge_label(iq, "YES", confidence=0.8, model_binary_id="edge-key")

    with pytest.raises(ApiException) as e:
        gl_experimental.add_edge_label(iq, "NO", confidence=0.8, model_binary_id="edge-key")
    assert e.value.status == HTTPStatus.CONFLICT


@retry_on_failure()
def test_edge_label_on_count_detector(gl_experimental: ExperimentalApi, detector_name: Callable):
    det = gl_experimental.create_counting_detector(
        detector_name("Test edge count labels"), "test_query", "test_object_class"
    )
    iq = gl_experimental.submit_image_query(det, "test/assets/cat.jpeg")
    roi = gl_experimental.create_roi(label="test_object_class", top_left=(0.1, 0.1), bottom_right=(0.6, 0.6))
    roi.score = 0.7

    gl_experimental.add_edge_label(iq, 1, confidence=0.8, model_binary_id="edge-key", rois=[roi])

    with pytest.raises(ApiException) as e:
        gl_experimental.add_edge_label(iq, 0, confidence=0.8, model_binary_id="edge-key", rois=[])
    assert e.value.status == HTTPStatus.CONFLICT
