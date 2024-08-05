from datetime import datetime

import PIL
from groundlight import ExperimentalApi


def test_get_image(gl_experimental: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    det = gl_experimental.get_or_create_detector(name, "test_query")
    iq = gl_experimental.submit_image_query(det, image="test/assets/dog.jpeg", wait=10)
    gl_experimental.get_image(iq.id)
    assert isinstance(PIL.Image.open(gl_experimental.get_image(iq.id)), PIL.Image.Image)
