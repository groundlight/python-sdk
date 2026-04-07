from typing import Callable

import PIL
from groundlight import ExperimentalApi

from test.retry_decorator import retry_on_failure


@retry_on_failure()
def test_get_image(gl_experimental: ExperimentalApi, detector_name: Callable):
    det = gl_experimental.get_or_create_detector(detector_name(), "test_query")
    iq = gl_experimental.submit_image_query(det, image="test/assets/dog.jpeg", wait=10)
    gl_experimental.get_image(iq.id)
    assert isinstance(PIL.Image.open(gl_experimental.get_image(iq.id)), PIL.Image.Image)
