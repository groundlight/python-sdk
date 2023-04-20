"""Defines the possible values for binary class labels like YES/NO or PASS/FAIL.
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
    # Should this be an error?
    logger.warning(f"Unrecognized internal label {label} - leaving alone.")
    return label


def convert_display_label_to_internal(
    context: Union[ImageQuery, Detector, str],  # pylint: disable=unused-argument
    label: str,
) -> str:
    # NOTE: In the future we should validate against actually supported labels for the detector
    if not isinstance(label, str):
        raise ValueError(f"Expected a string label, but got {label} of type {type(label)}")
    upper = label.upper()
    if upper == Label.YES:
        return DeprecatedLabel.PASS.value
    if upper == Label.NO:
        return DeprecatedLabel.FAIL.value
    # TODO: Should we support adding an "UNSURE" label in the SDK?
    raise ValueError(f'Invalid label string "{label}".  Must be one of {Label.YES.value},{Label.NO.value}.')


def is_valid_display_result(result: Any, strict: bool = False) -> bool:
    if not isinstance(result, ClassificationResult):
        return False
    if not is_valid_display_label(result.label, strict=strict):
        return False
    return True


def is_valid_display_label(label: str, strict: bool = False) -> bool:
    if not strict:
        label = label.upper()
    return label in VALID_DISPLAY_LABELS
