# Optional star-imports are weird and not usually recommended ...
# ruff: noqa: F403,F405
# pylint: disable=wildcard-import,unused-wildcard-import,redefined-outer-name,import-outside-toplevel
import tempfile
from io import BytesIO

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


def test_bytestream_from_filename():
    images_streams = []
    images_streams.append(bytestream_from_filename("test/assets/cat.jpeg"))
    images_streams.append(bytestream_from_filename("test/assets/cat.png"))
    images_streams.append(bytestream_from_filename("test/assets/cat.png", jpeg_quality=95))
    for i in images_streams:
        assert isinstance(i, ByteStreamWrapper)
        image = Image.open(i)
        assert image.mode == "RGB"

    # pixel based test, verified the image is correct by eye, then got a pixel whose value to check against
    png_bytestream = bytestream_from_filename("test/assets/cat.png", jpeg_quality=95)
    png_image = Image.open(png_bytestream)
    assert png_image.getpixel((200, 200)) == (215, 209, 197)


def test_unsupported_image_type():
    with pytest.raises(TypeError):
        parse_supported_image_types(1)  # type: ignore

    with pytest.raises(TypeError):
        parse_supported_image_types(None)  # type: ignore

    with pytest.raises(TypeError):
        parse_supported_image_types(pytest)  # type: ignore


@pytest.mark.skipif(MISSING_PIL, reason="Needs pillow")  # type: ignore
def test_pil_support():
    from PIL import Image

    img = Image.new("RGB", (640, 480))
    jpeg = parse_supported_image_types(img)
    assert isinstance(jpeg, ByteStreamWrapper)

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


def test_byte_stream_wrapper():
    """
    Test that we can call `open` and `close` repeatedly many times on a
    ByteStreamWrapper and get the same output.
    """

    def run_test(byte_stream: ByteStreamWrapper):
        previous_bytes = byte_stream.read()

        current_attempt, total_attempts = 0, 5

        while current_attempt < total_attempts:
            new_bytes = byte_stream.read()
            assert new_bytes == previous_bytes
            byte_stream.close()

            current_attempt += 1

    image = "test/assets/dog.jpeg"
    buffer = buffer_from_jpeg_file(image_filename=image)

    buffered_reader = ByteStreamWrapper(data=buffer)
    with open(image, "rb") as image_file:
        bytes_io = ByteStreamWrapper(data=BytesIO(image_file.read()))

    run_test(buffered_reader)
    run_test(bytes_io)
