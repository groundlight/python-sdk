import imghdr
import io


def buffer_from_jpeg_file(image_filename: str) -> io.BufferedReader:
    """
    Get a buffer from an jpeg image file.

    For now, we only support JPEG files, and raise an ValueError otherwise.
    """
    if imghdr.what(image_filename) == "jpeg":
        return open(image_filename, "rb")
    else:
        raise ValueError("We only support JPEG files, for now.")


def jpeg_from_numpy(img:np.ndarray, jpeg_quality: int = 95) -> io.BytesIO:
    """Converts a numpy array to BytesIO
    """
    pilim = Image.fromarray(img.astype('uint8'), 'RGB')
    with io.BytesIO() as buf:
        pilim.save(buf, "jpeg", quality=jpeg_quality)
        #out = buf.getvalue()
        return out
