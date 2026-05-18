# pylint: disable=deprecated-module
from io import BufferedReader, BytesIO, IOBase
from pathlib import Path
from typing import Union

from groundlight.optional_imports import Image, np

DEFAULT_JPEG_QUALITY = 95

# The Groundlight cloud applies a recompress/shrink step on ingest. Doing the same
# work client-side saves bandwidth and ensures Edge Endpoints, which do not run
# this step, see the same input distribution that cloud-trained models expect.
#
# The constants and algorithm below mirror zuuul's implementation. Source of truth:
#   - zuuul/janzu/apparati/imgtools.py::recompress_shrink_image
#   - zuuul/janzu/reef_api/utils.py::_save_image (gate)
#   - zuuul/janzu/authz/user-settings-defaults.yaml (default values)
# If the cloud's behavior changes, update these together.
MAX_BYTES_IMAGE_SIZE = 256_000
MAX_IMAGE_RESOLUTION_LONGSIDE = 1024
RECOMPRESS_SHRINK_IMAGE_JPEG_QUALITY = 85


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


def recompress_shrink_image(jpeg: bytes) -> bytes:
    """Shrink and re-encode an oversized JPEG to match the cloud's ingest pipeline.

    If the input is already at or below MAX_BYTES_IMAGE_SIZE, returns it unchanged.
    Otherwise, decodes the image, scales it (BICUBIC, aspect-ratio preserved) so the
    longest side is at most MAX_IMAGE_RESOLUTION_LONGSIDE, and re-encodes as JPEG.

    Already-lossy JPEGs are decoded and re-encoded, which is the same lossy step the
    cloud has been doing for years; net quality reaching the ML pipeline is unchanged.
    """
    if len(jpeg) <= MAX_BYTES_IMAGE_SIZE:
        return jpeg
    img = Image.open(BytesIO(jpeg)).convert("RGB")
    if max(img.size) > MAX_IMAGE_RESOLUTION_LONGSIDE:
        ratio = MAX_IMAGE_RESOLUTION_LONGSIDE / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, resample=Image.Resampling.BICUBIC)
    buf = BytesIO()
    img.save(buf, "jpeg", quality=RECOMPRESS_SHRINK_IMAGE_JPEG_QUALITY)
    return buf.getvalue()


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
