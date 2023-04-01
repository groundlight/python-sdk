import imghdr
from io import BufferedReader, BytesIO
from typing import Union

from groundlight.optional_imports import Image, np


def buffer_from_jpeg_file(image_filename: str) -> BufferedReader:
    """
    Get a buffer from an jpeg image file.

    For now, we only support JPEG files, and raise an ValueError otherwise.
    """
    if imghdr.what(image_filename) == "jpeg":
        # Note this will get fooled by truncated binaries since it only reads the header.
        # That's okay - the server will catch it.
        return open(image_filename, "rb")
    else:
        raise ValueError("We only support JPEG files, for now.")


def jpeg_from_numpy(img: np.ndarray, jpeg_quality: int = 95) -> bytes:
    """Converts a numpy array to BytesIO"""
    pilim = Image.fromarray(img.astype("uint8"), "RGB")
    with BytesIO() as buf:
        buf = BytesIO()
        pilim.save(buf, "jpeg", quality=jpeg_quality)
        out = buf.getvalue()
        return out


def parse_supported_image_types(
    image: Union[str, bytes, BytesIO, BufferedReader, np.ndarray]
) -> Union[BytesIO, BufferedReader]:
    """Parse the supported image types into BytesIO"""
    if isinstance(image, str):
        # Assume it is a filename
        return buffer_from_jpeg_file(image)
    elif isinstance(image, bytes):
        # Create a BytesIO object
        return BytesIO(image)
    elif isinstance(image, Image.Image):
        # Save PIL image as jpeg in BytesIO
        jpeg = BytesIO()
        image.save(jpeg, "jpeg")
        return jpeg
    elif isinstance(image, BytesIO) or isinstance(image, BufferedReader):
        # Already in the right format
        return image
    elif isinstance(image, np.ndarray):
        return BytesIO(jpeg_from_numpy(image))
    else:
        raise TypeError(
            "Unsupported type for image. We only support numpy arrays (3,W,H) or JPEG images specified through a filename, bytes, BytesIO, or BufferedReader object."
        )
