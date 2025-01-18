from datetime import datetime

import pytest
from groundlight import ExperimentalApi
from groundlight_openapi_client.exceptions import NotFoundException


def test_create_action(gl_experimental: ExperimentalApi):
    # We first clear out any rules in case the account has any left over from a previous test
    gl_experimental.delete_all_rules()
    name = f"Test {datetime.utcnow()}"
    det = gl_experimental.get_or_create_detector(name, "test_query")
    rule = gl_experimental.create_rule(det, f"test_rule_{name}", "EMAIL", "test@example.com")
    rule2 = gl_experimental.get_rule(rule.id)
    assert rule == rule2


@pytest.mark.skip(reason="actions are global on account, the test matrix collides with itself")  # type: ignore
def test_get_all_actions(gl_experimental: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    num_test_rules = 13  # needs to be larger than the default page size
    gl_experimental.ITEMS_PER_PAGE = 10
    assert gl_experimental.ITEMS_PER_PAGE < num_test_rules
    det = gl_experimental.get_or_create_detector(name, "test_query")
    gl_experimental.delete_all_rules()
    for i in range(num_test_rules):
        _ = gl_experimental.create_rule(det, f"test_rule_{i}", "EMAIL", "test@example.com")
    rules = gl_experimental.list_rules(page_size=gl_experimental.ITEMS_PER_PAGE)
    assert rules.count == num_test_rules
    assert len(rules.results) == gl_experimental.ITEMS_PER_PAGE
    num_deleted = gl_experimental.delete_all_rules()
    assert num_deleted == num_test_rules
    rules = gl_experimental.list_rules()
    assert rules.count == 0


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


def test_create_alert_multiple_actions(gl_experimental: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    det = gl_experimental.get_or_create_detector(name, "test_query")
    condition = gl_experimental.make_condition("CHANGED_TO", {"label": "YES"})
    action1 = gl_experimental.make_action("EMAIL", "test@groundlight.ai", False)
    action2 = gl_experimental.make_action("EMAIL", "test@groundlight.ai", False)
    actions = [action1, action2]
    alert = gl_experimental.create_alert(
        det,
        f"test_alert_{name}",
        condition,
        actions,
    )
    assert len(alert.action.root) == len(actions)


def test_create_alert_webhook_action(gl_experimental: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    det = gl_experimental.get_or_create_detector(name, "test_query")
    condition = gl_experimental.make_condition("ANSWERED_CONSECUTIVELY", {"num_consecutive_labels": 1, "label": "YES"})
    webhook_url = "https://hooks.slack.com/services/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"
    webhook_action = gl_experimental.make_webhook_action(webhook_url, include_image=False)
    alert = gl_experimental.create_alert(
        det,
        f"test_alert_{name}",
        condition,
        webhook_actions=webhook_action,
    )
    assert len(alert.webhook_action) == 1
    assert len(alert.action.root) == 0


def test_create_alert_multiple_webhook_actions(gl_experimental: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    det = gl_experimental.get_or_create_detector(name, "test_query")
    condition = gl_experimental.make_condition("CHANGED_TO", {"label": "YES"})
    webhook_action_1 = gl_experimental.make_webhook_action("https://groundlight.ai", include_image=True)
    webhook_action_2 = gl_experimental.make_webhook_action("https://example.com/webhook", include_image=False)
    webhook_actions = [webhook_action_1, webhook_action_2]
    alert = gl_experimental.create_alert(det, f"test_alert_{name}", condition, webhook_actions=webhook_actions)
    assert len(alert.webhook_action) == len(webhook_actions)
    assert len(alert.action.root) == 0


def test_create_alert_webhook_action_and_other_action(gl_experimental: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    det = gl_experimental.get_or_create_detector(name, "test_query")
    condition = gl_experimental.make_condition("CHANGED_TO", {"label": "YES"})
    webhook_action = gl_experimental.make_webhook_action("https://groundlight.ai", include_image=True)
    email_action = gl_experimental.make_action("EMAIL", "test@groundlight.ai", False)
    alert = gl_experimental.create_alert(
        det, f"test_alert_{name}", condition, webhook_actions=webhook_action, actions=email_action
    )
    assert len(alert.webhook_action) == 1
    assert len(alert.action.root) == 1
