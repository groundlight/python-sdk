import pytest
from groundlight import ExperimentalApi
from openapi_client.exceptions import NotFoundException


def test_create_action(gl: ExperimentalApi):
    det = gl.get_or_create_detector("testing_detector", "test_query")
    rule = gl.create_rule(det, "test_rule", "EMAIL", "test@example.com")
    rule2 = gl.get_rule(rule.id)
    assert rule == rule2
    gl.delete_rule(rule.id)
    with pytest.raises(NotFoundException) as _:
        gl.get_rule(rule.id)


@pytest.mark.skip(reason="actions are global on account, the test matrix collides with itself")  # type: ignore
def test_get_all_actions(gl: ExperimentalApi):
    num_test_rules = 13  # needs to be larger than the default page size
    gl.ITEMS_PER_PAGE = 10
    assert gl.ITEMS_PER_PAGE < num_test_rules
    det = gl.get_or_create_detector("test_detector", "test_query")
    gl.delete_all_rules()
    for i in range(num_test_rules):
        _ = gl.create_rule(det, f"test_rule_{i}", "EMAIL", "test@example.com")
    rules = gl.list_rules(page_size=gl.ITEMS_PER_PAGE)
    assert rules.count == num_test_rules
    assert len(rules.results) == gl.ITEMS_PER_PAGE
    num_deleted = gl.delete_all_rules()
    assert num_deleted == num_test_rules
    rules = gl.list_rules()
    assert rules.count == 0
