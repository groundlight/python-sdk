"""
    Groundlight API

    Groundlight makes it simple to understand images. You can easily create computer vision detectors just by describing what you want to know using natural language.  # noqa: E501

    The version of the OpenAPI document: 0.15.3
    Contact: support@groundlight.ai
    Generated by: https://openapi-generator.tech
"""

import sys
import unittest

import groundlight_openapi_client
from groundlight_openapi_client.model.roi_request import ROIRequest

globals()["ROIRequest"] = ROIRequest
from groundlight_openapi_client.model.label_value_request import LabelValueRequest


class TestLabelValueRequest(unittest.TestCase):
    """LabelValueRequest unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testLabelValueRequest(self):
        """Test LabelValueRequest"""
        # FIXME: construct object with mandatory attributes with example values
        # model = LabelValueRequest()  # noqa: E501
        pass


if __name__ == "__main__":
    unittest.main()
