from groundlight import ExperimentalApi
from groundlight.internalapi import iq_is_answered, iq_is_confident

def test_iq_is_confident(gl_experimental: ExperimentalApi):
    det = gl_experimental.get_or_create_detector("Test", "test_query")
    iq = gl_experimental.ask_async(det, image="test/assets/dog.jpeg", wait=10)
    assert not iq_is_confident(iq, 0.9)

def test_iq_is_answered(gl_experimental: ExperimentalApi):
    det = gl_experimental.get_or_create_detector("Test", "test_query")
    iq = gl_experimental.ask_async(det, image="test/assets/dog.jpeg", wait=10)
    assert not iq_is_answered(iq)

