import pytest

from groundlight.images import *
from groundlight.optional_imports import *


@pytest.mark.skipif(MISSING_NUMPY or MISSING_PIL, reason="Needs numpy and pillow")
def test_jpeg_from_numpy():
    np_img = np.random.uniform(0, 255, (480, 640, 3))
    jpeg1 = jpeg_from_numpy(np_img)
    assert len(jpeg1) > 500

    np_img = np.random.uniform(0, 255, (768, 1024, 3))
    jpeg2 = jpeg_from_numpy(np_img)
    assert len(jpeg2) > len(jpeg1)

    np_img = np.random.uniform(0, 255, (768, 1024, 3))
    jpeg3 = jpeg_from_numpy(np_img, jpeg_quality=50)
    assert len(jpeg2) > len(jpeg3)


@pytest.mark.skipif(MISSING_PIL, reason="Needs pillow")
def test_pil_support():
    from PIL import Image

    img = Image.new("RGB", (640, 480))
    jpeg = parse_supported_image_types(img)
    assert isinstance(jpeg, BytesIO)
