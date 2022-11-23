import pytest

from groundlight import Groundlight


def test_mocked_image_query(mocker):
    # mocker is a fixture defined by pytest-mock
    mocker.patch("openapi_client.api.image_queries_api.ImageQueriesApi.submit_image_query")
    gl = Groundlight()
    # TODO: submit an image query and check that it gets called


def test_blocking_submit():
    # TODO: call the blocking API, and verify that the service gets called a bunch of times.
    pass
