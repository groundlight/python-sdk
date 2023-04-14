# Optional star-imports are weird and not usually recommended ...
# ruff: noqa: F403,F405
# pylint: disable=wildcard-import,unused-wildcard-import,redefined-outer-name,import-outside-toplevel
import tempfile

import pytest
from groundlight.images import *
from groundlight.optional_imports import *

JPEG_MIN_SIZE = 500


@pytest.mark.skipif(MISSING_NUMPY or MISSING_PIL, reason="Needs numpy and pillow")  # type: ignore
def test_jpeg_from_numpy():
    np_img = np.random.uniform(0, 255, (480, 640, 3))
    jpeg1 = jpeg_from_numpy(np_img)
    assert len(jpeg1) > JPEG_MIN_SIZE

    np_img = np.random.uniform(0, 255, (768, 1024, 3))
    jpeg2 = jpeg_from_numpy(np_img)
    assert len(jpeg2) > len(jpeg1)

    np_img = np.random.uniform(0, 255, (768, 1024, 3))
    jpeg3 = jpeg_from_numpy(np_img, jpeg_quality=50)
    assert len(jpeg2) > len(jpeg3)


def test_unsupported_image_type():
    with pytest.raises(TypeError):
        parse_supported_image_types(1)

    with pytest.raises(TypeError):
        parse_supported_image_types(None)

    with pytest.raises(TypeError):
        parse_supported_image_types(pytest)


@pytest.mark.skipif(MISSING_PIL, reason="Needs pillow")  # type: ignore
def test_pil_support():
    from PIL import Image

    img = Image.new("RGB", (640, 480))
    jpeg = parse_supported_image_types(img)
    assert isinstance(jpeg, BytesIO)

    # Now try to parse the BytesIO object as an image
    jpeg_bytes = jpeg.getvalue()
    # save the image to a tempfile
    with tempfile.TemporaryFile() as f:
        f.write(jpeg_bytes)
        f.seek(0)
        img2 = Image.open(f)
        assert img2.size == (640, 480)


@pytest.mark.skipif(MISSING_PIL, reason="Needs pillow")  # type: ignore
def test_pil_support_ref():
    # Similar to test_pil_support, but uses a known-good file
    from PIL import Image

    fn = "test/assets/dog.jpeg"
    parsed = parse_supported_image_types(fn)
    # Now try to parse the BytesIO object as an image
    jpeg_bytes = parsed.read()
    # save the image to a tempfile
    with tempfile.TemporaryFile() as f:
        f.write(jpeg_bytes)
        f.seek(0)
        img2 = Image.open(f)
        assert img2.size == (509, 339)
