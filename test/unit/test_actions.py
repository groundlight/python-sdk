from datetime import datetime

import pytest
from groundlight import ExperimentalApi
from groundlight_openapi_client.exceptions import NotFoundException


def test_create_action(gl_experimental: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    det = gl_experimental.get_or_create_detector(name, "test_query")
    rule = gl_experimental.create_rule(det, f"test_rule_{name}", "EMAIL", "test@example.com")
    rule2 = gl_experimental.get_rule(rule.id)
    assert rule == rule2


def test_get_all_actions(gl_experimental: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    num_test_rules = 13  # needs to be larger than the default page size
    gl_experimental.ITEMS_PER_PAGE = 10
    assert gl_experimental.ITEMS_PER_PAGE < num_test_rules
    det = gl_experimental.get_or_create_detector(name, "test_query")
    for i in range(num_test_rules):
        _ = gl_experimental.create_rule(det, f"test_rule_{i}", "EMAIL", "test@example.com")
    rules = gl_experimental.list_rules(page_size=gl_experimental.ITEMS_PER_PAGE)
    # The exact number of actions is not guaranteed if another client is making calls at the same time
    assert rules.count > num_test_rules
    assert len(rules.results) == gl_experimental.ITEMS_PER_PAGE

def test_delete_actions():
    name = f"Test {datetime.utcnow()}"
    num_test_rules = 13  # needs to be larger than the default page size
    # TODO: get actions by detector

def test_create_action_with_human_review(gl_experimental: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    det = gl_experimental.get_or_create_detector(name, "test_query")
    rule = gl_experimental.create_rule(
        det, f"test_rule_{name}", "EMAIL", "test@example.com", human_review_required=True
    )
    rule2 = gl_experimental.get_rule(rule.id)
    assert rule == rule2


@pytest.mark.skip(reason="actions are global on account, the test matrix collides with itself")  # type: ignore
def test_delete_action(gl_experimental: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    det = gl_experimental.get_or_create_detector(name, "test_query")
    rule = gl_experimental.create_rule(det, f"test_rule_{name}", "EMAIL", "test@example.com")
    gl_experimental.delete_rule(rule.id)
    with pytest.raises(NotFoundException) as _:
        gl_experimental.get_rule(rule.id)
