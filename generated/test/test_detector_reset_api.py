"""
    Groundlight API

    Groundlight makes it simple to understand images. You can easily create computer vision detectors just by describing what you want to know using natural language.  # noqa: E501

    The version of the OpenAPI document: 0.15.3
    Contact: support@groundlight.ai
    Generated by: https://openapi-generator.tech
"""

import unittest

import groundlight_openapi_client
from groundlight_openapi_client.api.detector_reset_api import DetectorResetApi  # noqa: E501


class TestDetectorResetApi(unittest.TestCase):
    """DetectorResetApi unit test stubs"""

    def setUp(self):
        self.api = DetectorResetApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_reset_detector(self):
        """Test case for reset_detector"""
        pass


if __name__ == "__main__":
    unittest.main()
