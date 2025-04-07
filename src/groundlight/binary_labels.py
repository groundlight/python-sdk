"""Defines the possible values for binary class labels like YES/NO.
Provides methods to convert between them.

This part of the API is kinda ugly right now.  So we'll encapsulate the ugliness in one place.
"""

import logging
from enum import Enum
from typing import Union

from model import Detector, ImageQuery

logger = logging.getLogger(__name__)


class Label(str, Enum):
    YES = "YES"
    NO = "NO"
    UNCLEAR = "UNCLEAR"


VALID_DISPLAY_LABELS = {Label.YES, Label.NO, Label.UNCLEAR}


class DeprecatedLabel(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    UNSURE = "__UNSURE"


DEPRECATED_LABEL_NAMES = {
    DeprecatedLabel.PASS,
    DeprecatedLabel.FAIL,
    DeprecatedLabel.NEEDS_REVIEW,
    DeprecatedLabel.UNSURE,
}


def convert_internal_label_to_display(
    context: Union[ImageQuery, Detector, str],  # pylint: disable=unused-argument
    label: str,
) -> Union[Label, str]:
    """Convert a label that comes from our API into the label string enum that we show to the user.

    NOTE: We return UPPERCASE label strings to the user, unless there is a custom label (which
    shouldn't be happening at this time).
    """
    # NOTE: We should be able to do nothing here now, keeping for radiation proofing
    if not isinstance(label, str) and not isinstance(label, Label):
        raise ValueError(f"Expected a string label, but got {label} of type {type(label)}")
    upper = label.upper()
    if upper in {Label.YES, DeprecatedLabel.PASS}:
        return Label.YES
    if upper in {Label.NO, DeprecatedLabel.FAIL}:
        return Label.NO
    if upper in {Label.UNCLEAR, DeprecatedLabel.NEEDS_REVIEW, DeprecatedLabel.UNSURE}:
        return Label.UNCLEAR

    logger.warning(f"Unrecognized internal label {label} - leaving it alone as a string.")
    return label
