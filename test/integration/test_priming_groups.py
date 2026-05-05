"""
Tests for PrimingGroup and ML pipeline methods on ExperimentalApi.

The create/get/delete priming group tests are marked @pytest.mark.expensive because they
require training a detector (submit 8 labeled images, wait ~90s) before a pipeline has a
trained_at timestamp that indicates it can seed a PrimingGroup.  Run them explicitly with:

    pytest -m expensive test/unit/test_priming_groups.py
"""

import time

import pytest
from groundlight import ExperimentalApi
from groundlight.internalapi import NotFoundError
from model import MLPipeline, ModeEnum, PrimingGroup

# ---------------------------------------------------------------------------
# list_detector_pipelines
# ---------------------------------------------------------------------------


def test_list_detector_pipelines_returns_list(gl_experimental: ExperimentalApi, detector):
    """A freshly created detector has at least one pipeline."""
    pipelines = gl_experimental.list_detector_pipelines(detector)
    assert len(pipelines.results) >= 1
    assert all(isinstance(p, MLPipeline) for p in pipelines.results)


def test_list_detector_pipelines_accepts_detector_id_string(gl_experimental: ExperimentalApi, detector):
    """list_detector_pipelines should accept a raw ID string as well as a Detector object."""
    by_obj = gl_experimental.list_detector_pipelines(detector)
    by_id = gl_experimental.list_detector_pipelines(detector.id)
    assert [p.id for p in by_obj.results] == [p.id for p in by_id.results]


def test_list_detector_pipelines_unknown_detector_raises(gl_experimental: ExperimentalApi):
    with pytest.raises(NotFoundError):
        gl_experimental.list_detector_pipelines("det_doesnotexist000000000000")


# ---------------------------------------------------------------------------
# list_priming_groups
# ---------------------------------------------------------------------------


def test_list_priming_groups_returns_list(gl_experimental: ExperimentalApi):
    groups = gl_experimental.list_priming_groups()
    assert all(isinstance(g, PrimingGroup) for g in groups.results)


# ---------------------------------------------------------------------------
# create / get / delete  (expensive — require a trained pipeline)
# ---------------------------------------------------------------------------


def _wait_for_trained_pipeline(gl_experimental: ExperimentalApi, detector, timeout: int = 90) -> MLPipeline:
    """
    Submit 4 dog images (labeled YES) and 4 cat images (labeled NO), then poll until the active
    pipeline has a trained_at timestamp (i.e. has been trained).  Raises TimeoutError if training
    doesn't complete within `timeout` seconds.
    """
    # Submit 4 dog images with YES labels
    for _ in range(4):
        iq = gl_experimental.submit_image_query(detector, "test/assets/dog.jpeg", human_review="NEVER")
        gl_experimental.add_label(iq, "YES")

    # Submit 4 cat images with NO labels
    for _ in range(4):
        iq = gl_experimental.submit_image_query(detector, "test/assets/cat.jpeg", human_review="NEVER")
        gl_experimental.add_label(iq, "NO")

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        pipelines = gl_experimental.list_detector_pipelines(detector)
        for p in pipelines.results:
            if p.is_active_pipeline and p.trained_at is not None:
                return p
        time.sleep(5)

    raise TimeoutError(f"Detector {detector.id} did not produce a trained pipeline within {timeout}s")


@pytest.mark.expensive
def test_create_priming_group(gl_experimental: ExperimentalApi, detector):
    trained = _wait_for_trained_pipeline(gl_experimental, detector)

    pg = gl_experimental.create_priming_group(
        name=f"test-primer-{detector.id}",
        source_ml_pipeline_id=trained.id,
        detector_mode=ModeEnum.BINARY,
        canonical_query="Is there a dog?",
    )

    assert isinstance(pg, PrimingGroup)
    assert pg.id.startswith("pg_")
    assert pg.name == f"test-primer-{detector.id}"
    assert pg.canonical_query == "Is there a dog?"
    assert pg.is_global is False

    # cleanup
    gl_experimental.delete_priming_group(pg.id)


@pytest.mark.expensive
def test_create_priming_group_disable_shadow_pipelines(gl_experimental: ExperimentalApi, detector):
    trained = _wait_for_trained_pipeline(gl_experimental, detector)

    pg = gl_experimental.create_priming_group(
        name=f"test-primer-noshadow-{detector.id}",
        source_ml_pipeline_id=trained.id,
        detector_mode=ModeEnum.BINARY,
        disable_shadow_pipelines=True,
    )

    assert pg.disable_shadow_pipelines is True

    gl_experimental.delete_priming_group(pg.id)


@pytest.mark.expensive
def test_get_priming_group(gl_experimental: ExperimentalApi, detector):
    trained = _wait_for_trained_pipeline(gl_experimental, detector)

    pg = gl_experimental.create_priming_group(
        name=f"test-primer-get-{detector.id}",
        source_ml_pipeline_id=trained.id,
        detector_mode=ModeEnum.BINARY,
    )

    fetched = gl_experimental.get_priming_group(pg.id)
    assert fetched.id == pg.id
    assert fetched.name == pg.name

    gl_experimental.delete_priming_group(pg.id)


@pytest.mark.expensive
def test_get_priming_group_unknown_raises(gl_experimental: ExperimentalApi):
    with pytest.raises(NotFoundError):
        gl_experimental.get_priming_group("pg_doesnotexist000000000000")


@pytest.mark.expensive
def test_delete_priming_group(gl_experimental: ExperimentalApi, detector):
    trained = _wait_for_trained_pipeline(gl_experimental, detector)

    pg = gl_experimental.create_priming_group(
        name=f"test-primer-del-{detector.id}",
        source_ml_pipeline_id=trained.id,
        detector_mode=ModeEnum.BINARY,
    )

    gl_experimental.delete_priming_group(pg.id)

    with pytest.raises(NotFoundError):
        gl_experimental.get_priming_group(pg.id)


@pytest.mark.expensive
def test_created_priming_group_appears_in_list(gl_experimental: ExperimentalApi, detector):
    trained = _wait_for_trained_pipeline(gl_experimental, detector)

    pg = gl_experimental.create_priming_group(
        name=f"test-primer-list-{detector.id}",
        source_ml_pipeline_id=trained.id,
        detector_mode=ModeEnum.BINARY,
    )

    groups = gl_experimental.list_priming_groups()
    assert any(g.id == pg.id for g in groups.results)

    gl_experimental.delete_priming_group(pg.id)
