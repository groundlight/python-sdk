"""
Tests for PrimingGroup and ML pipeline methods on ExperimentalApi.

The create/get/delete priming group tests are marked @pytest.mark.expensive because they
require training a detector (submit 8 labeled images, wait ~90s) before a pipeline has a
trained_at timestamp that indicates it can seed a PrimingGroup.  Run them explicitly with:

    pytest -m expensive test/unit/test_priming_groups.py
"""

import time
from unittest.mock import MagicMock, patch

import pytest
from groundlight import ExperimentalApi
from groundlight.internalapi import NotFoundError
from model import MLPipeline, PrimingGroup

# ---------------------------------------------------------------------------
# list_detector_pipelines
# ---------------------------------------------------------------------------


def test_list_detector_pipelines_returns_list(gl_experimental: ExperimentalApi, detector):
    """A freshly created detector has at least one pipeline."""
    pipelines = gl_experimental.list_detector_pipelines(detector)
    assert isinstance(pipelines, list)
    assert len(pipelines) >= 1
    assert all(isinstance(p, MLPipeline) for p in pipelines)


def test_list_detector_pipelines_accepts_detector_id_string(gl_experimental: ExperimentalApi, detector):
    """list_detector_pipelines should accept a raw ID string as well as a Detector object."""
    by_obj = gl_experimental.list_detector_pipelines(detector)
    by_id = gl_experimental.list_detector_pipelines(detector.id)
    assert [p.id for p in by_obj] == [p.id for p in by_id]


def test_list_detector_pipelines_unknown_detector_raises(gl_experimental: ExperimentalApi):
    with pytest.raises(NotFoundError):
        gl_experimental.list_detector_pipelines("det_doesnotexist000000000000")


# ---------------------------------------------------------------------------
# list_priming_groups
# ---------------------------------------------------------------------------


def test_list_priming_groups_returns_list(gl_experimental: ExperimentalApi):
    groups = gl_experimental.list_priming_groups()
    assert isinstance(groups, list)
    assert all(isinstance(g, PrimingGroup) for g in groups)


# ---------------------------------------------------------------------------
# create / get / delete  (mocked)
# ---------------------------------------------------------------------------

_MOCK_PIPELINE = {
    "id": "pipe_mock0000000000000001",
    "pipeline_config": "never-review",
    "is_active_pipeline": True,
    "is_edge_pipeline": False,
    "is_unclear_pipeline": False,
    "is_oodd_pipeline": False,
    "is_enabled": True,
    "created_at": "2024-01-01T00:00:00Z",
    "trained_at": "2024-01-01T01:00:00Z",
}

_MOCK_PG = {
    "id": "pg_mock0000000000000001",
    "name": "test-primer",
    "is_global": False,
    "canonical_query": "Is there a dog?",
    "active_pipeline_config": None,
    "priming_group_specific_shadow_pipeline_configs": None,
    "disable_shadow_pipelines": False,
    "created_at": "2024-01-01T00:00:00Z",
}


def _mock_response(status_code: int, json_body=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_body or {}
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        resp.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return resp


def test_create_priming_group_mocked(gl_experimental: ExperimentalApi):
    with patch("groundlight.experimental_api.requests.post") as mock_post:
        mock_post.return_value = _mock_response(201, _MOCK_PG)

        pg = gl_experimental.create_priming_group(
            name="test-primer",
            source_ml_pipeline_id="pipe_mock0000000000000001",
            canonical_query="Is there a dog?",
        )

    assert isinstance(pg, PrimingGroup)
    assert pg.id == "pg_mock0000000000000001"
    assert pg.name == "test-primer"
    assert pg.canonical_query == "Is there a dog?"
    assert pg.is_global is False
    mock_post.assert_called_once()
    _, kwargs = mock_post.call_args
    assert kwargs["json"]["name"] == "test-primer"
    assert kwargs["json"]["source_ml_pipeline_id"] == "pipe_mock0000000000000001"


def test_create_priming_group_disable_shadow_pipelines_mocked(gl_experimental: ExperimentalApi):
    pg_data = {**_MOCK_PG, "name": "test-primer-noshadow", "disable_shadow_pipelines": True}
    with patch("groundlight.experimental_api.requests.post") as mock_post:
        mock_post.return_value = _mock_response(201, pg_data)

        pg = gl_experimental.create_priming_group(
            name="test-primer-noshadow",
            source_ml_pipeline_id="pipe_mock0000000000000001",
            disable_shadow_pipelines=True,
        )

    assert pg.disable_shadow_pipelines is True
    _, kwargs = mock_post.call_args
    assert kwargs["json"]["disable_shadow_pipelines"] is True


def test_get_priming_group_mocked(gl_experimental: ExperimentalApi):
    with patch("groundlight.experimental_api.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, _MOCK_PG)

        pg = gl_experimental.get_priming_group("pg_mock0000000000000001")

    assert isinstance(pg, PrimingGroup)
    assert pg.id == "pg_mock0000000000000001"
    assert pg.name == "test-primer"


def test_get_priming_group_unknown_raises_mocked(gl_experimental: ExperimentalApi):
    with patch("groundlight.experimental_api.requests.get") as mock_get:
        mock_get.return_value = _mock_response(404)

        with pytest.raises(NotFoundError):
            gl_experimental.get_priming_group("pgp_doesnotexist000000000000")


def test_delete_priming_group_mocked(gl_experimental: ExperimentalApi):
    with (
        patch("groundlight.experimental_api.requests.get") as mock_get,
        patch("groundlight.experimental_api.requests.delete") as mock_delete,
    ):
        mock_get.return_value = _mock_response(410)
        mock_delete.return_value = _mock_response(204)

        gl_experimental.delete_priming_group("pg_mock0000000000000001")

        # After deletion, getting it should raise NotFoundError (410 Gone)
        with pytest.raises(NotFoundError):
            gl_experimental.get_priming_group("pg_mock0000000000000001")

    mock_delete.assert_called_once()


def test_created_priming_group_appears_in_list_mocked(gl_experimental: ExperimentalApi):
    list_response = {"results": [_MOCK_PG]}
    with patch("groundlight.experimental_api.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, list_response)

        groups = gl_experimental.list_priming_groups()

    assert any(g.id == "pg_mock0000000000000001" for g in groups)


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
        for p in pipelines:
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
    )

    fetched = gl_experimental.get_priming_group(pg.id)
    assert fetched.id == pg.id
    assert fetched.name == pg.name

    gl_experimental.delete_priming_group(pg.id)


@pytest.mark.expensive
def test_get_priming_group_unknown_raises(gl_experimental: ExperimentalApi):
    with pytest.raises(NotFoundError):
        gl_experimental.get_priming_group("pgp_doesnotexist000000000000")


@pytest.mark.expensive
def test_delete_priming_group(gl_experimental: ExperimentalApi, detector):
    trained = _wait_for_trained_pipeline(gl_experimental, detector)

    pg = gl_experimental.create_priming_group(
        name=f"test-primer-del-{detector.id}",
        source_ml_pipeline_id=trained.id,
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
    )

    groups = gl_experimental.list_priming_groups()
    assert any(g.id == pg.id for g in groups)

    gl_experimental.delete_priming_group(pg.id)
