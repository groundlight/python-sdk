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
from groundlight_openapi_client.model.channel_enum import ChannelEnum

globals()["ChannelEnum"] = ChannelEnum
from groundlight_openapi_client.model.action import Action


class TestAction(unittest.TestCase):
    """Action unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testAction(self):
        """Test Action"""
        # FIXME: construct object with mandatory attributes with example values
        # model = Action()  # noqa: E501
        pass


if __name__ == "__main__":
    unittest.main()
