"""Defines the possible values for binary class labels like Yes/No or PASS/FAIL.
Provides methods to convert between them.

This part of the API is kinda ugly right now.  So we'll encapsulate the ugliness in one place.
"""
import logging
from typing import List, Union

from model import Detector, ImageQuery

logger = logging.getLogger("groundlight.sdk")


def internal_labels_for_detector(context: Union[ImageQuery, Detector, str]) -> List[str]:
    """Returns an ordered list of class labels as strings.
    These are the versions of labels that the API demands.
    :param context: Can be an ImageQuery, a Detector, or a string-id for one of them."""
    # TODO: At some point this will need to be an API call, because these will be defined per-detector
    return ["PASS", "FAIL"]


def convert_internal_label_to_display(context: Union[ImageQuery, Detector, str], label: str) -> str:
    # TODO: Someday we probably do nothing here.
    upper = label.upper()
    if upper == "PASS":
        return "YES"
    if upper == "FAIL":
        return "NO"
    if upper in ["YES", "NO"]:
        return label
    logger.warning(f"Unrecognized internal label {label} - leaving alone.")
    return label


def convert_display_label_to_internal(context: Union[ImageQuery, Detector, str], label: str) -> str:
    # TODO: Validate against actually supported labels for the detector
    upper = label.upper()
    if upper == "PASS" or upper == "YES":
        return "PASS"
    if upper == "FAIL" or upper == "NO":
        return "FAIL"
    raise ValueError(f'Invalid label string "{label}".  Must be one of YES,NO,PASS,FAIL')
