"""Tests for image handling behavior in Groundlight.submit_image_query."""

import inspect
from io import BytesIO
from unittest import mock

import pytest
from groundlight import ExperimentalApi, Groundlight
from groundlight.images import MAX_BYTES_IMAGE_SIZE, MAX_IMAGE_RESOLUTION_LONGSIDE
from groundlight.internalapi import InternalApiError
from PIL import Image
from utils import make_random_jpeg


def test_experimental_api_accepts_groundlight_constructor_args():
    """Ensures that ExperimentalApi declares all the same args as Groundlight.

    Extra args on ExperimentalApi are fine. This only compares parameter names.
    """
    groundlight_names = {name for name in inspect.signature(Groundlight.__init__).parameters if name != "self"}
    experimental_names = {name for name in inspect.signature(ExperimentalApi.__init__).parameters if name != "self"}
    missing = groundlight_names - experimental_names
    assert missing == set()


def test_submit_image_query_sends_shrunken_image(gl: Groundlight):
    """Verifies that image shrinking runs in the submission path by inspecting the bytes at the HTTP layer.

    Submits an oversized image to a mocked urllib3 transport, then checks that the body
    that actually went on the wire was already resized to the expected dimensions.
    """
    big = make_random_jpeg(4000, 3000)
    assert len(big) > MAX_BYTES_IMAGE_SIZE

    with mock.patch("urllib3.PoolManager.request") as mock_request:
        mock_request.return_value.status = 500
        with pytest.raises(InternalApiError):
            gl.submit_image_query(detector="det_test", image=big, wait=0)

    body = mock_request.call_args_list[0].kwargs["body"]
    sent_img = Image.open(BytesIO(body))
    assert max(sent_img.size) == MAX_IMAGE_RESOLUTION_LONGSIDE


def test_submit_image_query_sends_original_when_shrink_disabled(gl: Groundlight):
    """A client with shrinking off uploads the original dimensions."""
    big = make_random_jpeg(4000, 3000)
    assert len(big) > MAX_BYTES_IMAGE_SIZE
    original = Image.open(BytesIO(big))
    gl.shrink_oversized_images = False

    with mock.patch("urllib3.PoolManager.request") as mock_request:
        mock_request.return_value.status = 500
        with pytest.raises(InternalApiError):
            gl.submit_image_query(detector="det_test", image=big, wait=0)

    body = mock_request.call_args_list[0].kwargs["body"]
    sent_img = Image.open(BytesIO(body))
    assert sent_img.size == original.size
