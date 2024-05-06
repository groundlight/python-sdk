"""
    Groundlight API

    Groundlight makes it simple to understand images. You can easily create computer vision detectors just by describing what you want to know using natural language.  # noqa: E501

    The version of the OpenAPI document: 0.15.1
    Contact: support@groundlight.ai
    Generated by: https://openapi-generator.tech
"""


import unittest

import groundlight_openapi_client
from groundlight_openapi_client.api.notes_api import NotesApi  # noqa: E501


class TestNotesApi(unittest.TestCase):
    """NotesApi unit test stubs"""

    def setUp(self):
        self.api = NotesApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_create_note(self):
        """Test case for create_note"""
        pass

    def test_get_notes(self):
        """Test case for get_notes"""
        pass


if __name__ == "__main__":
    unittest.main()
