import io

from PIL import Image


def bytesio_from_jpeg_file(image_filename) -> io.BytesIO:
    """
    Get a BytesIO object from a JPEG filename.
    """
    img = Image.open(image_filename)
    with io.BytesIO() as buf:
        img.save(buf, "jpeg")
        _bytes = buf.getvalue()
    return io.BytesIO(_bytes)
