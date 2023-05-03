import imghdr
from io import BufferedReader, BytesIO
from typing import Union

from groundlight.optional_imports import Image, np


def buffer_from_jpeg_file(image_filename: str) -> BufferedReader:
    """Get a buffer from an jpeg image file.

    For now, we only support JPEG files, and raise an ValueError otherwise.
    """
    if imghdr.what(image_filename) == "jpeg":
        # Note this will get fooled by truncated binaries since it only reads the header.
        # That's okay - the server will catch it.
        return open(image_filename, "rb")
    raise ValueError("We only support JPEG files, for now.")


def jpeg_from_numpy(img: np.ndarray, jpeg_quality: int = 95) -> bytes:
    """Converts a numpy array to BytesIO."""
    pilim = Image.fromarray(img.astype("uint8"), "RGB")
    with BytesIO() as buf:
        pilim.save(buf, "jpeg", quality=jpeg_quality)
        out = buf.getvalue()
        return out


def parse_supported_image_types(
    image: Union[str, bytes, Image.Image, BytesIO, BufferedReader, np.ndarray],
    jpeg_quality: int = 95,
) -> Union[BytesIO, BufferedReader]:
    """Parse the many supported image types into a bytes-stream objects.
    In some cases we have to JPEG compress.
    """
    if isinstance(image, str):
        # Assume it is a filename
        return buffer_from_jpeg_file(image)
    if isinstance(image, bytes):
        # Create a BytesIO object
        return BytesIO(image)
    if isinstance(image, Image.Image):
        # Save PIL image as jpeg in BytesIO
        bytesio = BytesIO()
        image.save(bytesio, "jpeg", quality=jpeg_quality)
        bytesio.seek(0)
        return bytesio
    if isinstance(image, (BytesIO, BufferedReader)):
        # Already in the right format
        return image
    if isinstance(image, np.ndarray):
        # Assume it is in BGR format from opencv
        return BytesIO(jpeg_from_numpy(image[:, :, ::-1], jpeg_quality=jpeg_quality))
    raise TypeError(
        (
            "Unsupported type for image. Must be PIL, numpy (H,W,3) RGB, or a JPEG as a filename (str), bytes,"
            " BytesIO, or BufferedReader."
        ),
    )
