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
    num_test_rules = 15
    num_rules_per_page = 10
    assert num_rules_per_page < num_test_rules
    det = gl.get_or_create_detector("test_detector", "test_query")
    gl.delete_all_rules()
    for i in range(num_test_rules):
        _ = gl.create_rule(det, f"test_rule_{i}", "EMAIL", "test@example.com")
    rules = gl.list_rules(page_size=num_rules_per_page)
    assert rules.count == num_test_rules
    assert len(rules.results) == num_rules_per_page
    gl.delete_all_rules()
    rules = gl.list_rules()
    assert rules.count == 0
