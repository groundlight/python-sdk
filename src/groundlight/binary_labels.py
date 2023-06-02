"""Defines the possible values for binary class labels like YES/NO.
Provides methods to convert between them.

This part of the API is kinda ugly right now.  So we'll encapsulate the ugliness in one place.
"""
import logging
from enum import Enum
from typing import Optional, Union

from model import Detector, ImageQuery, PartialImageQuery

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
) -> Union[Label, str]:
    """Convert a label that comes from our API into the label string enum that we show to the user.

    NOTE: We return UPPERCASE label strings to the user, unless there is a custom label (which
    shouldn't be happening at this time).
    """
    # NOTE: Someday we will do nothing here, when the server provides properly named classes.
    if not isinstance(label, str):
        raise ValueError(f"Expected a string label, but got {label} of type {type(label)}")
    upper = label.upper()
    if upper in {Label.YES, DeprecatedLabel.PASS}:
        return Label.YES
    if upper in {Label.NO, DeprecatedLabel.FAIL}:
        return Label.NO
    if upper in {Label.UNSURE, DeprecatedLabel.NEEDS_REVIEW}:
        return Label.UNSURE

    logger.warning(f"Unrecognized internal label {label} - leaving it alone as a string.")
    return label


def convert_display_label_to_internal(
    context: Union[ImageQuery, Detector, str],  # pylint: disable=unused-argument
    label: Union[Label, str],
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

    raise ValueError(f"Invalid label string '{label}'.  Must be one of '{Label.YES.value}','{Label.NO.value}'.")


def map_result(iq: ImageQuery, threshold: float) -> str:
    """Interprets the result of an image query and returns a string
    representing the answer, or "UNSURE" if the confidence is below the threshold.
    Maps old-style PASS/FAIL labels to YES/NO if needed.
    """
    if (iq.result.confidence is not None) and (iq.result.confidence < threshold):
        answer = "UNSURE"
    else:
        answer = iq.result.label

    ANSWER_MAP = {
        "PASS": "YES",
        "FAIL": "NO",
    }
    if answer in ANSWER_MAP:
        answer = ANSWER_MAP[answer]
    return answer


def is_guess_confident(iq: PartialImageQuery, confidence_threshold: Optional[float]) -> bool:
    """Returns True if the confidence of the guess is above the threshold."""
    if iq.result.confidence is None:
        # Currently we don't have a confidence value for human labels.
        # So this indicates a human label, which we're currently treating as confident.
        return True
    if confidence_threshold is None:
        # I'm not sure why confidence_threshold is allowed to be None
        # But we can't compare it.
        # To be safe, we say that we're not confident.
        return False
    return iq.result.confidence >= confidence_threshold
