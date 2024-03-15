import pytest
from groundlight import ExperimentalApi
from openapi_client.exceptions import NotFoundException


@pytest.fixture(name="gl")
def _gl() -> ExperimentalApi:
    return ExperimentalApi()


def test_create_action(gl: ExperimentalApi):
    det = gl.get_or_create_detector("test_detector", "test_query")
    rule = gl.create_rule(det, "test_rule", "EMAIL", "test@example.com")
    rule2 = gl.get_rule(rule.id)
    assert rule == rule2
    gl.delete_rule(rule.id)
    with pytest.raises(NotFoundException) as _:
        gl.get_rule(rule.id)


def test_get_all_rules(gl: ExperimentalApi):
    det = gl.get_or_create_detector("test_detector", "test_query")
    gl.delete_all_rules()
    for i in range(10):
        _ = gl.create_rule(det, f"test_rule_{i}", "EMAIL", "test@example.com")
    rules = gl.get_rules_list()
    assert len(rules) == 10
    gl.delete_all_rules()
    rules = gl.get_rules_list()
    assert len(rules) == 0
