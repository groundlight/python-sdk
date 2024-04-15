from datetime import datetime

import PIL
from groundlight import ExperimentalApi


def test_get_image(gl: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    det = gl.get_or_create_detector(name, "test_query")
    iq = gl.submit_image_query(det, image="test/assets/dog.jpeg", wait=10)
    gl.get_image(iq.id)
    assert isinstance(PIL.Image.open(gl.get_image(iq.id)), PIL.Image.Image)
