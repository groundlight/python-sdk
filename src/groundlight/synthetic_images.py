"""Support types for synthetic image generation."""

import base64

from model import SyntheticImage
from pydantic import Field, field_serializer, field_validator

# Generation runs an image model, so waiting for a response takes considerably longer than a
# typical API call. This is a read budget rather than a budget for the whole request: it must
# outlast the server's own read timeout so its error response arrives instead of the SDK giving
# up first, while staying inside the server's worker timeout.
DEFAULT_SYNTHETIC_IMAGE_READ_TIMEOUT = 90.0

# Establishing the connection is unrelated to how long generation takes, so it gets the short
# budget that keeps an unreachable host from waiting out the read timeout.
DEFAULT_SYNTHETIC_IMAGE_CONNECT_TIMEOUT = 10.0

# The image is the entire request body, and the server caps a request body at 10MiB
# (DATA_UPLOAD_MAX_MEMORY_SIZE), rejecting anything larger.
MAX_SYNTHETIC_IMAGE_BYTES = 10 * 1024 * 1024


class SyntheticImageResult(SyntheticImage):  # pylint: disable=too-few-public-methods
    """A generated synthetic image and its ground-truth annotations.

    Identical to the wire model except that ``image`` holds the decoded PNG bytes rather
    than a base64 string, so it can be written to disk or resubmitted directly.
    """

    image: bytes = Field(..., min_length=1, description="The generated image, as decoded PNG bytes.")

    @field_validator("image", mode="before")
    @classmethod
    def _decode_image(cls, value):
        """Decode the wire model's base64 into the bytes this field promises.

        Without this, pydantic's lax mode would accept the base64 string and ASCII-encode it,
        storing the text instead of the image and raising nothing -- so the guard belongs here
        rather than in each caller.
        """
        return base64.b64decode(value, validate=True) if isinstance(value, str) else value

    @field_serializer("image", when_used="json")
    def _serialize_image(self, value: bytes) -> str:
        """Re-encode as base64 for JSON, which cannot carry raw bytes."""
        return base64.b64encode(value).decode("ascii")
