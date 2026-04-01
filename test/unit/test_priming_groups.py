from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from groundlight import ExperimentalApi
from groundlight.internalapi import NotFoundError
from model import MLPipeline, PrimingGroup

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MOCK_PIPELINE_DATA = {
    "id": "pipe_abc123",
    "pipeline_config": "never-review",
    "cached_vizlogic_key": "mlb_testkey1234",
    "is_active_pipeline": True,
    "is_edge_pipeline": False,
    "is_unclear_pipeline": False,
    "is_oodd_pipeline": False,
    "is_enabled": True,
    "created_at": "2026-01-01T00:00:00Z",
    "trained_at": None,
}

MOCK_PRIMING_GROUP_DATA = {
    "id": "pgp_abc123",
    "name": "door-detector-primer",
    "is_global": False,
    "canonical_query": "Is the door open?",
    "active_pipeline_config": None,
    "active_pipeline_base_mlbinary_key": "mlb_testkey1234",
    "priming_group_specific_shadow_pipeline_configs": None,
    "disable_shadow_pipelines": False,
    "created_at": "2026-01-01T00:00:00Z",
}


def _mock_response(status_code=200, json_data=None):
    resp = Mock()
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.raise_for_status.return_value = None
    return resp


def _mock_error_response(status_code):
    resp = Mock()
    resp.status_code = status_code
    resp.raise_for_status.side_effect = Exception(f"HTTP {status_code}")
    return resp


# ---------------------------------------------------------------------------
# list_detector_pipelines
# ---------------------------------------------------------------------------


def test_list_detector_pipelines_returns_pipelines():
    gl = ExperimentalApi()
    with patch("requests.get") as mock_get:
        mock_get.return_value = _mock_response(json_data={"results": [MOCK_PIPELINE_DATA], "count": 1})
        pipelines = gl.list_detector_pipelines("det_abc123")

    assert len(pipelines) == 1
    assert isinstance(pipelines[0], MLPipeline)
    assert pipelines[0].id == "pipe_abc123"
    assert pipelines[0].is_active_pipeline is True


def test_list_detector_pipelines_accepts_detector_object():
    gl = ExperimentalApi()
    detector = Mock()
    detector.id = "det_abc123"
    with patch("requests.get") as mock_get:
        mock_get.return_value = _mock_response(json_data={"results": [MOCK_PIPELINE_DATA], "count": 1})
        pipelines = gl.list_detector_pipelines(detector)

    assert len(pipelines) == 1
    assert mock_get.call_args[0][0].endswith("/v1/detectors/det_abc123/pipelines")


def test_list_detector_pipelines_empty():
    gl = ExperimentalApi()
    with patch("requests.get") as mock_get:
        mock_get.return_value = _mock_response(json_data={"results": [], "count": 0})
        pipelines = gl.list_detector_pipelines("det_abc123")

    assert pipelines == []


def test_list_detector_pipelines_404_raises_not_found():
    gl = ExperimentalApi()
    with patch("requests.get") as mock_get:
        mock_get.return_value = _mock_error_response(404)
        with pytest.raises(NotFoundError, match="det_notexist"):
            gl.list_detector_pipelines("det_notexist")


# ---------------------------------------------------------------------------
# list_priming_groups
# ---------------------------------------------------------------------------


def test_list_priming_groups_returns_groups():
    gl = ExperimentalApi()
    with patch("requests.get") as mock_get:
        mock_get.return_value = _mock_response(json_data={"results": [MOCK_PRIMING_GROUP_DATA], "count": 1})
        groups = gl.list_priming_groups()

    assert len(groups) == 1
    assert isinstance(groups[0], PrimingGroup)
    assert groups[0].id == "pgp_abc123"
    assert groups[0].name == "door-detector-primer"


def test_list_priming_groups_empty():
    gl = ExperimentalApi()
    with patch("requests.get") as mock_get:
        mock_get.return_value = _mock_response(json_data={"results": [], "count": 0})
        groups = gl.list_priming_groups()

    assert groups == []


def test_list_priming_groups_hits_correct_url():
    gl = ExperimentalApi()
    with patch("requests.get") as mock_get:
        mock_get.return_value = _mock_response(json_data={"results": [], "count": 0})
        gl.list_priming_groups()

    called_url = mock_get.call_args[0][0]
    assert called_url.endswith("/v1/priming-groups")


# ---------------------------------------------------------------------------
# create_priming_group
# ---------------------------------------------------------------------------


def test_create_priming_group_returns_group():
    gl = ExperimentalApi()
    with patch("requests.post") as mock_post:
        mock_post.return_value = _mock_response(json_data=MOCK_PRIMING_GROUP_DATA)
        pg = gl.create_priming_group(
            name="door-detector-primer",
            source_ml_pipeline_id="pipe_abc123",
            canonical_query="Is the door open?",
        )

    assert isinstance(pg, PrimingGroup)
    assert pg.id == "pgp_abc123"
    assert pg.name == "door-detector-primer"
    assert pg.canonical_query == "Is the door open?"


def test_create_priming_group_sends_correct_payload():
    gl = ExperimentalApi()
    with patch("requests.post") as mock_post:
        mock_post.return_value = _mock_response(json_data=MOCK_PRIMING_GROUP_DATA)
        gl.create_priming_group(
            name="door-detector-primer",
            source_ml_pipeline_id="pipe_abc123",
            canonical_query="Is the door open?",
            disable_shadow_pipelines=True,
        )

    payload = mock_post.call_args[1]["json"]
    assert payload["name"] == "door-detector-primer"
    assert payload["source_ml_pipeline_id"] == "pipe_abc123"
    assert payload["canonical_query"] == "Is the door open?"
    assert payload["disable_shadow_pipelines"] is True


def test_create_priming_group_omits_canonical_query_when_none():
    gl = ExperimentalApi()
    with patch("requests.post") as mock_post:
        mock_post.return_value = _mock_response(json_data=MOCK_PRIMING_GROUP_DATA)
        gl.create_priming_group(name="primer", source_ml_pipeline_id="pipe_abc123")

    payload = mock_post.call_args[1]["json"]
    assert "canonical_query" not in payload


def test_create_priming_group_disable_shadow_pipelines_default_false():
    gl = ExperimentalApi()
    with patch("requests.post") as mock_post:
        mock_post.return_value = _mock_response(json_data=MOCK_PRIMING_GROUP_DATA)
        gl.create_priming_group(name="primer", source_ml_pipeline_id="pipe_abc123")

    payload = mock_post.call_args[1]["json"]
    assert payload["disable_shadow_pipelines"] is False


# ---------------------------------------------------------------------------
# get_priming_group
# ---------------------------------------------------------------------------


def test_get_priming_group_returns_group():
    gl = ExperimentalApi()
    with patch("requests.get") as mock_get:
        mock_get.return_value = _mock_response(json_data=MOCK_PRIMING_GROUP_DATA)
        pg = gl.get_priming_group("pgp_abc123")

    assert isinstance(pg, PrimingGroup)
    assert pg.id == "pgp_abc123"
    assert pg.name == "door-detector-primer"


def test_get_priming_group_404_raises_not_found():
    gl = ExperimentalApi()
    with patch("requests.get") as mock_get:
        mock_get.return_value = _mock_error_response(404)
        with pytest.raises(NotFoundError, match="pgp_notexist"):
            gl.get_priming_group("pgp_notexist")


def test_get_priming_group_hits_correct_url():
    gl = ExperimentalApi()
    with patch("requests.get") as mock_get:
        mock_get.return_value = _mock_response(json_data=MOCK_PRIMING_GROUP_DATA)
        gl.get_priming_group("pgp_abc123")

    called_url = mock_get.call_args[0][0]
    assert called_url.endswith("/v1/priming-groups/pgp_abc123")


# ---------------------------------------------------------------------------
# delete_priming_group
# ---------------------------------------------------------------------------


def test_delete_priming_group_succeeds():
    gl = ExperimentalApi()
    with patch("requests.delete") as mock_delete:
        mock_delete.return_value = _mock_response(status_code=204)
        gl.delete_priming_group("pgp_abc123")  # should not raise

    mock_delete.assert_called_once()


def test_delete_priming_group_404_raises_not_found():
    gl = ExperimentalApi()
    with patch("requests.delete") as mock_delete:
        mock_delete.return_value = _mock_error_response(404)
        with pytest.raises(NotFoundError, match="pgp_notexist"):
            gl.delete_priming_group("pgp_notexist")


def test_delete_priming_group_hits_correct_url():
    gl = ExperimentalApi()
    with patch("requests.delete") as mock_delete:
        mock_delete.return_value = _mock_response(status_code=204)
        gl.delete_priming_group("pgp_abc123")

    called_url = mock_delete.call_args[0][0]
    assert called_url.endswith("/v1/priming-groups/pgp_abc123")
