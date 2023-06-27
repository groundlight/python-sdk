import imghdr
from io import BufferedReader, BytesIO, IOBase
from typing import Union

from groundlight.optional_imports import Image, np


class ByteStreamWrapper(IOBase):
    """This class acts as a thin wrapper around bytes in order to
    maintain files in an open state. This is useful, in particular,
    when we want to retry accessing the file without having to re-open it.
    """

    def __init__(self, data: Union[BufferedReader, BytesIO, bytes]) -> None:
        super().__init__()
        if isinstance(data, (BufferedReader, BytesIO)):
            self._data = data.read()
        else:
            self._data = data

    def read(self) -> bytes:
        return self._data

    def getvalue(self) -> bytes:
        return self._data

    def close(self) -> None:
        pass


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
) -> ByteStreamWrapper:
    """Parse the many supported image types into a bytes-stream objects.
    In some cases we have to JPEG compress.
    """
    if isinstance(image, str):
        # Assume it is a filename
        buffer = buffer_from_jpeg_file(image)
        return ByteStreamWrapper(data=buffer)
    if isinstance(image, bytes):
        # Create a BytesIO object
        return ByteStreamWrapper(data=image)
    if isinstance(image, Image.Image):
        # Save PIL image as jpeg in BytesIO
        bytesio = BytesIO()
        image.save(bytesio, "jpeg", quality=jpeg_quality)
        bytesio.seek(0)
        return ByteStreamWrapper(data=bytesio)
    if isinstance(image, (BytesIO, BufferedReader)):
        # Already in the right format
        return ByteStreamWrapper(data=image)
    if isinstance(image, np.ndarray):
        # Assume it is in BGR format from opencv
        return ByteStreamWrapper(data=jpeg_from_numpy(image[:, :, ::-1], jpeg_quality=jpeg_quality))
    raise TypeError(
        (
            "Unsupported type for image. Must be PIL, numpy (H,W,3) BGR, or a JPEG as a filename (str), bytes,"
            " BytesIO, or BufferedReader."
        ),
    )
