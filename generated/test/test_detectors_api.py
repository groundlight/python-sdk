"""
    Groundlight API

    Groundlight makes it simple to understand images. You can easily create computer vision detectors just by describing what you want to know using natural language.  # noqa: E501

    The version of the OpenAPI document: 0.15.3
    Contact: support@groundlight.ai
    Generated by: https://openapi-generator.tech
"""

import unittest

import groundlight_openapi_client
from groundlight_openapi_client.api.detectors_api import DetectorsApi  # noqa: E501


class TestDetectorsApi(unittest.TestCase):
    """DetectorsApi unit test stubs"""

    def setUp(self):
        self.api = DetectorsApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_create_detector(self):
        """Test case for create_detector"""
        pass

    def test_create_detector_group2(self):
        """Test case for create_detector_group2"""
        pass

    def test_delete_detector(self):
        """Test case for delete_detector"""
        pass

    def test_get_detector(self):
        """Test case for get_detector"""
        pass

    def test_get_detector_groups2(self):
        """Test case for get_detector_groups2"""
        pass

    def test_list_detectors(self):
        """Test case for list_detectors"""
        pass


if __name__ == "__main__":
    unittest.main()
