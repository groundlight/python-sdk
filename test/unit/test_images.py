import pytest
import PIL
from groundlight import ExperimentalApi


@pytest.fixture(name="gl")
def _gl() -> ExperimentalApi:
    return ExperimentalApi("https://api.dev.groundlight.ai")


def test_get_image(gl: ExperimentalApi):
    det = gl.get_or_create_detector("test_detector", "test_query")
    iq = gl.submit_image_query(det, image="test/assets/dog.jpeg", wait=10)
    gl.get_image(iq.id)
    assert isinstance(PIL.Image.open(gl.get_image(iq.id)), PIL.Image.Image)
