from groundlight import ExperimentalApi
from groundlight.internalapi import iq_is_answered, iq_is_confident
from groundlight_openapi_client import ImageQuery


def test_iq_is_confident(gl_experimental: ExperimentalApi, initial_iq: ImageQuery):
    det = gl_experimental.get_or_create_detector("Test", "test_query")
    iq = gl_experimental.ask_async(det, image="test/assets/dog.jpeg")
    assert not iq_is_confident(iq, 0.9)

    assert not iq_is_confident(initial_iq, 0.9)


def test_iq_is_answered(gl_experimental: ExperimentalApi, initial_iq: ImageQuery):
    det = gl_experimental.get_or_create_detector("Test", "test_query")
    iq = gl_experimental.ask_async(det, image="test/assets/dog.jpeg")
    assert not iq_is_answered(iq)

    assert not iq_is_answered(initial_iq)
