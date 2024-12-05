# pylint: disable=deprecated-module
from io import BufferedReader, BytesIO, IOBase
from pathlib import Path
from typing import Union

from groundlight.optional_imports import Image, np

DEFAULT_JPEG_QUALITY = 95


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


def bytestream_from_filename(image_filename: str, jpeg_quality: int = DEFAULT_JPEG_QUALITY) -> ByteStreamWrapper:
    """Determines what to do with an arbitrary filename

    Only supports JPEG and PNG files for now.
    For PNG files, we convert to RGB format used in JPEGs.
    """
    image_path = Path(image_filename)
    if image_path.suffix.lower() in (".jpeg", ".jpg"):
        buffer = buffer_from_jpeg_file(image_filename)
        return ByteStreamWrapper(data=buffer)
    if image_path.suffix.lower() == ".png":
        pil_img = Image.open(image_filename)
        # This chops off the alpha channel which can cause unexpected behavior, but handles minimal transparency well
        pil_img = pil_img.convert("RGB")
        return bytestream_from_pil(pil_image=pil_img, jpeg_quality=jpeg_quality)
    raise ValueError("We only support JPEG and PNG files, for now.")


def buffer_from_jpeg_file(image_filename: str) -> BufferedReader:
    """Get a buffer from an jpeg image file.

    For now, we only support JPEG files, and raise an ValueError otherwise.
    """
    if Path(image_filename).suffix.lower() in (".jpeg", ".jpg"):
        # Note this will get fooled by truncated binaries since it only reads the header.
        # That's okay - the server will catch it.
        return open(image_filename, "rb")
    raise ValueError("We only support JPEG files, for now.")


def jpeg_from_numpy(img: np.ndarray, jpeg_quality: int = DEFAULT_JPEG_QUALITY) -> bytes:
    """Converts a numpy array to BytesIO."""
    pilim = Image.fromarray(img.astype("uint8"), "RGB")
    with BytesIO() as buf:
        pilim.save(buf, "jpeg", quality=jpeg_quality)
        out = buf.getvalue()
        return out


def bytestream_from_pil(pil_image: Image.Image, jpeg_quality: int = DEFAULT_JPEG_QUALITY) -> ByteStreamWrapper:
    """Converts a PIL image to a BytesIO."""
    bytesio = BytesIO()
    pil_image.save(bytesio, "jpeg", quality=jpeg_quality)
    bytesio.seek(0)
    return ByteStreamWrapper(data=bytesio)


def parse_supported_image_types(
    image: Union[str, bytes, Image.Image, BytesIO, BufferedReader, np.ndarray],
    jpeg_quality: int = 95,
) -> ByteStreamWrapper:
    """Parse the many supported image types into a bytes-stream objects.
    In some cases we have to JPEG compress.
    """
    if isinstance(image, str):
        # Assume it is a filename
        return bytestream_from_filename(image_filename=image, jpeg_quality=jpeg_quality)
    if isinstance(image, bytes):
        # Create a BytesIO object
        return ByteStreamWrapper(data=image)
    if isinstance(image, Image.Image):
        # Save PIL image as jpeg in BytesIO
        return bytestream_from_pil(pil_image=image, jpeg_quality=jpeg_quality)
    if isinstance(image, (BytesIO, BufferedReader)):
        # Already in the right format
        return ByteStreamWrapper(data=image)
    if isinstance(image, np.ndarray):
        # Assume it is in BGR format from opencv
        return ByteStreamWrapper(data=jpeg_from_numpy(image[:, :, ::-1], jpeg_quality=jpeg_quality))
    raise TypeError(
        "Unsupported type for image. Must be PIL, numpy (H,W,3) BGR, or a JPEG as a filename (str), bytes,"
        " BytesIO, or BufferedReader.",
    )
