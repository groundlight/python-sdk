import base64
import json
import sys
from typing import Dict, Optional


def url_encode_dict(maybe_dict: Dict, name: str, size_limit_bytes: Optional[int] = None) -> str:
    """Encode a dictionary as a URL-safe, base64-encoded JSON string.

    :param maybe_dict: The dictionary to encode.
    :type maybe_dict: dict

    :param name: The name of the dictionary, for use in the error message.
    :type name: str

    :param size_limit_bytes: The maximum size of the dictionary, in bytes.
        If `None`, no size limit is enforced.
    :type size_limit_bytes: int or None

    :raises TypeError: If `maybe_dict` is not a dictionary.
    :raises ValueError: If `maybe_dict` is too large.

    :return: The URL-safe, base64-encoded JSON string.
    :rtype: str
    """
    if not isinstance(maybe_dict, dict):
        raise TypeError(f"`{name}` must be a dictionary: got {type(maybe_dict)}")

    data_json = json.dumps(maybe_dict)

    if size_limit_bytes is not None:
        size_bytes = sys.getsizeof(data_json)
        if size_bytes > size_limit_bytes:
            raise ValueError(f"`{name}` is too large: {size_bytes} bytes > {size_limit_bytes} bytes limit.")

    return base64.urlsafe_b64encode(data_json.encode("utf-8")).decode("utf-8")
