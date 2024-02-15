import base64
import json
from typing import Dict, Optional, Union


def url_encode_dict(maybe_dict: Union[Dict, str], name: str, size_limit_bytes: Optional[int] = None) -> str:
    """Encode a dictionary as a URL-safe, base64-encoded JSON string.

    :param maybe_dict: The dictionary or JSON string to encode.

    :param name: The name of the dictionary, for use in the error message.

    :param size_limit_bytes: The maximum size of the dictionary, in bytes.
        If `None`, no size limit is enforced.

    :raises TypeError: If `maybe_dict` is not a dictionary or JSON string.
    :raises ValueError: If `maybe_dict` is too large.

    :return: The URL-safe, base64-encoded JSON string.
    """
    original_type = type(maybe_dict)
    if isinstance(maybe_dict, str):
        try:
            # It's a little inefficient to parse the JSON string, just to re-encode it later. But it
            # allows us to check that we get a valid dictionary, and we remove any whitespace.
            maybe_dict = json.loads(maybe_dict)
        except json.JSONDecodeError as e:
            raise TypeError(f"`{name}` must be a dictionary or JSON string: got {original_type}") from e

    if not isinstance(maybe_dict, dict):
        raise TypeError(f"`{name}` must be a dictionary or JSON string: got {original_type}")

    data_json = json.dumps(maybe_dict)

    if size_limit_bytes is not None:
        size_bytes = len(data_json)
        if size_bytes > size_limit_bytes:
            raise ValueError(f"`{name}` is too large: {size_bytes} bytes > {size_limit_bytes} bytes limit.")

    return base64.urlsafe_b64encode(data_json.encode("utf-8")).decode("utf-8")
