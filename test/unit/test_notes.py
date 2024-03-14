import unittest

import PIL
from groundlight import ExperimentalApi


class TestNotes(unittest.TestCase):
    def setUp(self) -> None:
        self.gl = ExperimentalApi()
        return super().setUp()

    def test_notes(self):
        det = self.gl.get_or_create_detector("test_detector", "test_query")
        iq = self.gl.submit_image_query(det, image="test/assets/dog.jpeg", wait=10)
        # TODO
