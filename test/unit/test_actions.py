from datetime import datetime

import pytest
from groundlight import ApiException, ExperimentalApi
from model import Action


def test_create_alert_multiple_actions(gl_experimental: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    det = gl_experimental.get_or_create_detector(name, "test_query")
    condition = gl_experimental.make_condition("CHANGED_TO", {"label": "YES"})
    action1 = Action(channel="EMAIL", recipient="test@groundlight.ai", include_image=False)
    action2 = Action(channel="EMAIL", recipient="test@groundlight.ai", include_image=False)
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
    webhook_action_1 = gl_experimental.make_webhook_action(url="https://groundlight.ai", include_image=True)
    webhook_action_2 = gl_experimental.make_webhook_action(url="https://example.com/webhook", include_image=False)
    webhook_actions = [webhook_action_1, webhook_action_2]
    alert = gl_experimental.create_alert(det, f"test_alert_{name}", condition, webhook_actions=webhook_actions)
    assert len(alert.webhook_action) == len(webhook_actions)
    assert len(alert.action.root) == 0


def test_create_alert_webhook_action_and_other_action(gl_experimental: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    det = gl_experimental.get_or_create_detector(name, "test_query")
    condition = gl_experimental.make_condition("CHANGED_TO", {"label": "YES"})
    webhook_action = gl_experimental.make_webhook_action(url="https://groundlight.ai", include_image=True)
    email_action = Action(channel="EMAIL", recipient="test@groundlight.ai", include_image=False)
    alert = gl_experimental.create_alert(
        det, f"test_alert_{name}", condition, webhook_actions=webhook_action, actions=email_action
    )
    assert len(alert.webhook_action) == 1
    assert len(alert.action.root) == 1


def test_create_alert_webhook_action_with_payload_template(gl_experimental: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    det = gl_experimental.get_or_create_detector(name, "test_query")
    condition = gl_experimental.make_condition("CHANGED_TO", {"label": "YES"})
    payload_template = gl_experimental.make_payload_template('{"text": "This should be a valid payload"}')
    webhook_action = gl_experimental.make_webhook_action(
        url="https://hooks.slack.com/services/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",
        include_image=True,
        payload_template=payload_template,
    )
    alert = gl_experimental.create_alert(det, f"test_alert_{name}", condition, webhook_actions=webhook_action)

    assert len(alert.webhook_action) == 1
    assert alert.webhook_action[0].payload_template.template == '{"text": "This should be a valid payload"}'


def test_create_alert_webhook_action_with_invalid_payload_template(gl_experimental: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    det = gl_experimental.get_or_create_detector(name, "test_query")
    condition = gl_experimental.make_condition("CHANGED_TO", {"label": "YES"})
    payload_template = gl_experimental.make_payload_template(
        '{"text": "This should not be a valid payload, jinja brackets are not closed properly {{detector_id}"}'
    )
    webhook_action = gl_experimental.make_webhook_action(
        url="https://groundlight.ai", include_image=True, payload_template=payload_template
    )

    bad_request_exception_status_code = 400

    with pytest.raises(ApiException) as e:
        gl_experimental.create_alert(det, f"test_alert_{name}", condition, webhook_actions=webhook_action)
    assert e.value.status == bad_request_exception_status_code

    payload_template = gl_experimental.make_payload_template(
        "This should not be a valid payload, it's valid jinja but won't produce valid json"
    )
    webhook_action = gl_experimental.make_webhook_action(
        url="https://groundlight.ai", include_image=True, payload_template=payload_template
    )

    with pytest.raises(ApiException) as e:
        gl_experimental.create_alert(det, f"test_alert_{name}", condition, webhook_actions=webhook_action)
    assert e.value.status == bad_request_exception_status_code


def test_create_alert_webhook_action_headers(gl_experimental: ExperimentalApi):
    name = f"Test {datetime.utcnow()}"
    det = gl_experimental.get_or_create_detector(name, "test_query")
    condition = gl_experimental.make_condition("ANSWERED_CONSECUTIVELY", {"num_consecutive_labels": 1, "label": "YES"})

    test_api_key = "test_api_key"
    url = "https://example.com/webhook"
    headers = {
        "Authorization": f"Bearer {test_api_key}",
    }

    template = """{"records": [{"fields": {"detector_id": "{{ detector_id }}" } }]}"""

    payload_template = {"template": template, "headers": headers}
    webhook_action = gl_experimental.make_webhook_action(
        url=url, include_image=False, payload_template=payload_template
    )

    alert = gl_experimental.create_alert(
        det,
        f"test_alert_{name}",
        condition,
        webhook_actions=webhook_action,
    )

    assert len(alert.webhook_action) == 1
    assert alert.webhook_action[0].payload_template.template == template
    assert alert.webhook_action[0].payload_template.headers == headers


def test_create_invalid_payload_template_headers(gl_experimental: ExperimentalApi):
    with pytest.raises(Exception) as e:
        gl_experimental.make_payload_template(
            '{"template": "This is a fine template"}', headers="bad headers"  # type: ignore
        )
    assert e.typename == "ValidationError"
    assert "Input should be a valid dictionary" in str(e.value)
