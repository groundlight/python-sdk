"""
We collect various expensive tests here. These tests should not be run regularly.
"""

# Optional star-imports are weird and not usually recommended ...
# ruff: noqa: F403,F405
# pylint: disable=wildcard-import,unused-wildcard-import,redefined-outer-name,import-outside-toplevel
import json
import random
import string
import time
from datetime import datetime
from typing import Any, Dict, Optional, Union

import groundlight_openapi_client
import pytest
from groundlight import Groundlight
from groundlight.binary_labels import VALID_DISPLAY_LABELS, DeprecatedLabel, Label, convert_internal_label_to_display
from groundlight.internalapi import InternalApiError, NotFoundError, iq_is_answered, iq_is_confident
from groundlight.optional_imports import *
from groundlight.status_codes import is_user_error
from model import (
    BinaryClassificationResult,
    CountingResult,
    Detector,
    ImageQuery,
    PaginatedDetectorList,
    PaginatedImageQueryList,
)

DEFAULT_CONFIDENCE_THRESHOLD = 0.9
IQ_IMPROVEMENT_THRESHOLD = 0.75

@pytest.fixture(name="gl")
def fixture_gl() -> Groundlight:
    """Creates a Groundlight client object for testing."""
    _gl = Groundlight()
    _gl.DEFAULT_WAIT = 10
    return _gl

@pytest.mark.skip(reason="This test requires a human labeler who does not need to be in the testing loop")
def test_human_label(gl: Groundlight):
    detector = gl.create_detector(name=f"Test {datetime.utcnow()}", query="Is there a dog?")
    img_query = gl.submit_image_query(detector=detector.id, image="test/assets/dog.jpeg", wait=60, human_review="ALWAYS")

    count = 0
    while img_query.result.source == "ALGORITHM" or img_query.result.label == "STILL_PROCESSING":
        count += 1
        time.sleep(5)
        img_query = gl.get_image_query(img_query.id)
        if count > 12:
            assert False, f"Human review is taking too long: {img_query}"

    assert iq_is_answered(img_query)
    assert iq_is_confident(img_query, confidence_threshold=0.9)

@pytest.mark.skip(reason="This test can block development depending on the state of the service")
@pytest.mark.skipif(MISSING_PIL, reason="Needs pillow")  # type: ignore
def test_detector_improvement(gl: Groundlight):
    # test that we get confidence improvement after sending images in
    # Pass two of each type of image in
    import random
    import time

    from PIL import Image, ImageEnhance

    random.seed(2741)

    name = f"Test test_detector_improvement {datetime.utcnow()}"  # Need a unique name
    query = "Is there a dog?"
    detector = gl.create_detector(name=name, query=query)

    def submit_noisy_image(image, label=None):
        sharpness = ImageEnhance.Sharpness(image)
        noisy_image = sharpness.enhance(random.uniform(0.75, 1.25))
        color = ImageEnhance.Color(noisy_image)
        noisy_image = color.enhance(random.uniform(0.75, 1))
        contrast = ImageEnhance.Contrast(noisy_image)
        noisy_image = contrast.enhance(random.uniform(0.75, 1))
        brightness = ImageEnhance.Brightness(noisy_image)
        noisy_image = brightness.enhance(random.uniform(0.75, 1))
        img_query = gl.submit_image_query(detector=detector.id, image=noisy_image, wait=0, human_review="NEVER")
        if label is not None:
            gl.add_label(img_query, label)
        return img_query

    dog = Image.open("test/assets/dog.jpeg")
    cat = Image.open("test/assets/cat.jpeg")

    submit_noisy_image(dog, "YES")
    submit_noisy_image(dog, "YES")
    submit_noisy_image(cat, "NO")
    submit_noisy_image(cat, "NO")

    # wait to give enough time to train
    wait_period = 30  # seconds
    num_wait_periods = 4  # 2 minutes total
    result_confidence = 0.6
    new_dog_query = None
    new_cat_query = None
    for _ in range(num_wait_periods):
        time.sleep(wait_period)
        new_dog_query = submit_noisy_image(dog)
        new_cat_query = submit_noisy_image(cat)
        new_cat_result_confidence = new_cat_query.result.confidence
        new_dog_result_confidence = new_dog_query.result.confidence

        if (
            new_cat_result_confidence and new_cat_result_confidence < result_confidence
        ) or new_cat_query.result.label == "YES":
            # If the new query is not confident enough, we'll try again
            continue
        elif (
            new_dog_result_confidence and new_dog_result_confidence < result_confidence
        ) or new_dog_query.result.label == "NO":
            # If the new query is not confident enough, we'll try again
            continue
        else:
            assert True
            return

    assert (
        False
    ), f"The detector {detector} quality has not improved after two minutes q.v. {new_dog_query}, {new_cat_query}"


@pytest.mark.skip(
    reason="We don't yet have an SLA level to test ask_confident against, and the test is flakey as a result"
)
def test_ask_method_quality(gl: Groundlight, detector: Detector):
    # asks for some level of quality on how fast ask_ml is and that we will get a confident result from ask_confident
    fast_always_yes_iq = gl.ask_ml(detector=detector.id, image="test/assets/dog.jpeg", wait=0)
    assert iq_is_answered(fast_always_yes_iq)
    name = f"Test {datetime.utcnow()}"  # Need a unique name
    query = "Is there a dog?"
    detector = gl.create_detector(name=name, query=query, confidence_threshold=0.8)
    fast_iq = gl.ask_ml(detector=detector.id, image="test/assets/dog.jpeg", wait=0)
    assert iq_is_answered(fast_iq)
    confident_iq = gl.ask_confident(detector=detector.id, image="test/assets/dog.jpeg", wait=180)
    assert confident_iq.result.confidence is None or (confident_iq.result.confidence > IQ_IMPROVEMENT_THRESHOLD)
