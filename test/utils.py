"""Shared utility functions for tests."""

import os
from io import BytesIO

from PIL import Image


def make_random_jpeg(width: int, height: int, quality: int = 95) -> bytes:
    """Generate a JPEG with random pixel data."""
    img = Image.frombytes("RGB", (width, height), os.urandom(width * height * 3))
    buf = BytesIO()
    img.save(buf, "jpeg", quality=quality)
    return buf.getvalue()
