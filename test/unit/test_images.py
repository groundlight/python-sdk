import unittest

import PIL
from groundlight import ExperimentalApi


class TestImages(unittest.TestCase):
    def setUp(self) -> None:
        # self.gl = ExperimentalApi()
        self.gl = ExperimentalApi("https://api.dev.groundlight.ai/")
        return super().setUp()

    def test_get_image(self):
        det = self.gl.get_or_create_detector("test_detector", "test_query")
        iq = self.gl.submit_image_query(det, image="test/assets/dog.jpeg", wait=10)
        self.gl.get_image(iq.id)
        self.assertIsInstance(PIL.Image.open(self.gl.get_image(iq.id)), PIL.Image.Image)
