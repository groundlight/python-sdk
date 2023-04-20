"""Defines the possible values for binary class labels like YES/NO.
Provides methods to convert between them.

This part of the API is kinda ugly right now.  So we'll encapsulate the ugliness in one place.
"""
import logging
from enum import Enum
from typing import Any, Union

from model import ClassificationResult, Detector, ImageQuery

logger = logging.getLogger(__name__)


class Label(str, Enum):
    YES = "YES"
    NO = "NO"
    UNSURE = "UNSURE"


VALID_DISPLAY_LABELS = {Label.YES, Label.NO, Label.UNSURE}


class DeprecatedLabel(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NEEDS_REVIEW = "NEEDS_REVIEW"


DEPRECATED_LABEL_NAMES = {DeprecatedLabel.PASS, DeprecatedLabel.FAIL, DeprecatedLabel.NEEDS_REVIEW}


def convert_internal_label_to_display(
    context: Union[ImageQuery, Detector, str],  # pylint: disable=unused-argument
    label: str,
) -> str:
    """Convert a label that comes from our API into the label string that we show to the user.

    NOTE: We return UPPERCASE label strings to the user, unless there is a custom label (which
    shouldn't be happening at this time).
    """
    # NOTE: Someday we will do nothing here, when the server provides properly named classes.
    if not isinstance(label, str):
        raise ValueError(f"Expected a string label, but got {label} of type {type(label)}")
    upper = label.upper()
    if upper in {Label.YES, DeprecatedLabel.PASS}:
        return Label.YES.value
    if upper in {Label.NO, DeprecatedLabel.FAIL}:
        return Label.NO.value
    if upper in {Label.UNSURE, DeprecatedLabel.NEEDS_REVIEW}:
        return Label.UNSURE.value

    # Safety versus extensibility: should it be an error if we get an unrecognized internal label?
    logger.warning(f"Unrecognized internal label {label} - leaving alone.")

    return label


def convert_display_label_to_internal(
    context: Union[ImageQuery, Detector, str],  # pylint: disable=unused-argument
    label: str,
) -> str:
    """Convert a label that comes from the user into the label string that we send to the server. We
    are strict here, and only allow YES/NO.

    NOTE: We accept case-insensitive label strings from the user, but we send UPPERCASE labels to
    the server. E.g., user inputs "yes" -> the label is returned as "YES".
    """
    # NOTE: In the future we should validate against actually supported labels for the detector
    if not isinstance(label, str):
        raise ValueError(f"Expected a string label, but got {label} of type {type(label)}")
    upper = label.upper()
    if upper == Label.YES:
        return DeprecatedLabel.PASS.value
    if upper == Label.NO:
        return DeprecatedLabel.FAIL.value
    # TODO: Should we support the user adding an "UNSURE" label in the SDK?

    raise ValueError(f'Invalid label string "{label}".  Must be one of {Label.YES.value},{Label.NO.value}.')


def is_valid_display_result(result: Any) -> bool:
    """
    Is the image query result valid to display to the user?
    """
    if not isinstance(result, ClassificationResult):
        return False
    if not is_valid_display_label(result.label):
        return False
    return True


def is_valid_display_label(label: str) -> bool:
    """
    Is the image query result label valid to display to the user?
    """
    # NOTE: For now, we strictly only show UPPERCASE labels to the user.
    return label in VALID_DISPLAY_LABELS
