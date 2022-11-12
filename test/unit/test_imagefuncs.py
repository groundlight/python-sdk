import pytest

from groundlight.images import *

def test_jpeg_from_numpy():
    np_img = np.random.uniform(0, 255, (480, 640, 3))
    stream = jpeg_from_numpy(np_img)
    jpeg1 = stream.getvalue()
    assert len(jpeg1) > 500
    
    np_img = np.random.uniform(0, 255, (768, 1024, 3))
    stream = jpeg_from_numpy(np_img)
    jpeg2 = stream.getvalue()
    assert len(jpeg2) > len(jpeg1)

    np_img = np.random.uniform(0, 255, (768, 1024, 3))
    stream = jpeg_from_numpy(np_img, jpeg_quality=50)
    jpeg3 = stream.getvalue()
    assert len(jpeg2) > len(jpeg3)

