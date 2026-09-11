"""Support types for synthetic image generation.

Kept out of `experimental_api.py` so the generated `SyntheticImage` model can be
adapted without growing that module further.
"""

import base64
import binascii
import json
from typing import Any, Dict, Union

from model import SyntheticImage
from pydantic import Field, field_serializer

# Generation is a round trip through an image model, so it is far slower than a
# normal API call and needs its own default instead of DEFAULT_REQUEST_TIMEOUT.
DEFAULT_SYNTHETIC_IMAGE_TIMEOUT = 120.0

# The API documents lens_config as "up to 1KiB" of base64 url-safe encoded JSON.
# There is no maxLength in the spec, so this is enforced client-side against the
# encoded form -- that is what the query string actually carries.
LENS_CONFIG_MAX_ENCODED_BYTES = 1024


class SyntheticImageResult(SyntheticImage):
    """A generated synthetic image and its ground-truth annotations.

    Identical to the wire model except that ``image`` holds the decoded PNG bytes
    rather than a base64 string, so it can be written to disk or resubmitted
    directly. Serializing to JSON re-encodes it as base64.
    """

    image: bytes = Field(..., description="The generated image, as decoded PNG bytes.")

    @field_serializer("image", when_used="json")
    def _serialize_image(self, value: bytes) -> str:
        """Re-encode to base64 for JSON, which cannot carry raw bytes."""
        return base64.b64encode(value).decode("ascii")


def encode_lens_config(lens_config: Union[Dict[str, Any], str]) -> str:
    """Encode lens settings for the ``lens_config`` query parameter.

    :param lens_config: Either a dict to encode, a JSON string (recognized by a
        leading ``{``), or a string that is already base64 url-safe encoded JSON.

    :return: Base64 url-safe encoded JSON, with padding retained.
    :raises ValueError: If the value is not valid JSON, is not valid base64
        encoding valid JSON, or exceeds the size limit.
    """
    if isinstance(lens_config, str):
        stripped = lens_config.strip()
        if stripped.startswith("{"):
            try:
                lens_config = json.loads(stripped)
            except json.JSONDecodeError as e:
                raise ValueError(f"lens_config looks like JSON but could not be parsed: {e}") from e
        else:
            # Assume it is already encoded, but confirm rather than forwarding
            # something the server will only reject after a round trip.
            try:
                json.loads(base64.urlsafe_b64decode(stripped))
            except (binascii.Error, ValueError, UnicodeDecodeError) as e:
                raise ValueError(
                    "lens_config must be a dict, a JSON string, or base64 url-safe encoded JSON;"
                    f" could not decode it as the latter: {e}",
                ) from e
            return stripped

    # sort_keys makes the encoding deterministic for a given config.
    as_json = json.dumps(lens_config, separators=(",", ":"), sort_keys=True)
    encoded = base64.urlsafe_b64encode(as_json.encode("utf-8")).decode("ascii")
    if len(encoded) > LENS_CONFIG_MAX_ENCODED_BYTES:
        raise ValueError(
            f"lens_config is too large: {len(encoded)} bytes once encoded"
            f" ({len(as_json)} as JSON), but the limit is {LENS_CONFIG_MAX_ENCODED_BYTES}.",
        )
    return encoded
