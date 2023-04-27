"""Defines the possible values for binary class labels like YES/NO or PASS/FAIL.
Provides methods to convert between them.

This part of the API is kinda ugly right now.  So we'll encapsulate the ugliness in one place.
"""
import logging
from typing import List, Union

from model import Detector, ImageQuery

logger = logging.getLogger("groundlight.sdk")


PASS_DEPRECATED = "PASS"
FAIL_DEPRECATED = "FAIL"
YES = "YES"
NO = "NO"
DEPRECATED_LABEL_NAMES = {PASS_DEPRECATED, FAIL_DEPRECATED}


def internal_labels_for_detector(
    context: Union[ImageQuery, Detector, str],  # pylint: disable=unused-argument
) -> List[str]:
    """Returns an ordered list of class labels as strings.
    These are the versions of labels that the API demands.
    :param context: Can be an ImageQuery, a Detector, or a string-id for one of them.
    """
    # NOTE: At some point this will need to be an API call, because these will be defined per-detector
    return [PASS_DEPRECATED, FAIL_DEPRECATED]


def convert_internal_label_to_display(
    context: Union[ImageQuery, Detector, str],  # pylint: disable=unused-argument
    label: str,
) -> str:
    # NOTE: Someday we will do nothing here, when the server provides properly named classes.
    upper = label.upper()
    if upper == PASS_DEPRECATED:
        return YES
    if upper == FAIL_DEPRECATED:
        return NO
    if upper in {PASS_DEPRECATED, NO}:
        return label
    logger.warning(f"Unrecognized internal label {label} - leaving alone.")
    return label


def convert_display_label_to_internal(
    context: Union[ImageQuery, Detector, str],  # pylint: disable=unused-argument
    label: str,
) -> str:
    # NOTE: In the future we should validate against actually supported labels for the detector
    upper = label.upper()
    if upper in {PASS_DEPRECATED, YES}:
        return PASS_DEPRECATED
    if upper in {FAIL_DEPRECATED, NO}:
        return FAIL_DEPRECATED
    raise ValueError(f'Invalid label string "{label}".  Must be one of {YES},{NO},{PASS_DEPRECATED},{FAIL_DEPRECATED}')
