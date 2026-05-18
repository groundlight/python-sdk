"""Tests for image handling behavior in Groundlight.submit_image_query."""

from io import BytesIO
from unittest import mock

import pytest
from groundlight import Groundlight
from groundlight.images import MAX_BYTES_IMAGE_SIZE, MAX_IMAGE_RESOLUTION_LONGSIDE, jpeg_from_numpy
from groundlight.internalapi import InternalApiError
from groundlight.optional_imports import MISSING_NUMPY, MISSING_PIL, Image, np


@pytest.mark.skipif(MISSING_NUMPY or MISSING_PIL, reason="Needs numpy and pillow")  # type: ignore
def test_submit_image_query_sends_shrunken_image(gl: Groundlight):
    """Verifies that image shrinking runs in the submission path by inspecting the bytes at the HTTP layer.

    Submits an oversized image to a mocked urllib3 transport, then checks that the body
    that actually went on the wire was already resized to the expected dimensions.
    """
    np.random.seed(0)
    big = jpeg_from_numpy(np.random.uniform(0, 255, (3000, 4000, 3)))
    assert len(big) > MAX_BYTES_IMAGE_SIZE

    with mock.patch("urllib3.PoolManager.request") as mock_request:
        mock_request.return_value.status = 500
        with pytest.raises(InternalApiError):
            gl.submit_image_query(detector="det_test", image=big, wait=0)

    body = mock_request.call_args_list[0].kwargs["body"]
    sent_img = Image.open(BytesIO(body))
    assert max(sent_img.size) == MAX_IMAGE_RESOLUTION_LONGSIDE
