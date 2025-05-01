# pylint: disable=too-many-lines
"""
experimental_api.py

This module is part of our evolving SDK. While these functions are designed to provide valuable functionality to enhance
your projects, it's important to note that they are considered unstable. This means they may undergo significant
modifications or potentially be removed in future releases, which could lead to breaking changes in your applications.
"""

import json
from io import BufferedReader, BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import requests
from groundlight_openapi_client.api.actions_api import ActionsApi
from groundlight_openapi_client.api.detector_groups_api import DetectorGroupsApi
from groundlight_openapi_client.api.detector_reset_api import DetectorResetApi
from groundlight_openapi_client.api.edge_api import EdgeApi
from groundlight_openapi_client.api.image_queries_api import ImageQueriesApi
from groundlight_openapi_client.api.notes_api import NotesApi
from groundlight_openapi_client.model.action_request import ActionRequest
from groundlight_openapi_client.model.bounding_box_mode_configuration import BoundingBoxModeConfiguration
from groundlight_openapi_client.model.channel_enum import ChannelEnum
from groundlight_openapi_client.model.condition_request import ConditionRequest
from groundlight_openapi_client.model.count_mode_configuration import CountModeConfiguration
from groundlight_openapi_client.model.detector_group_request import DetectorGroupRequest
from groundlight_openapi_client.model.multi_class_mode_configuration import MultiClassModeConfiguration
from groundlight_openapi_client.model.patched_detector_request import PatchedDetectorRequest
from groundlight_openapi_client.model.payload_template_request import PayloadTemplateRequest
from groundlight_openapi_client.model.rule_request import RuleRequest
from groundlight_openapi_client.model.status_enum import StatusEnum
from groundlight_openapi_client.model.webhook_action_request import WebhookActionRequest
from model import (
    ROI,
    Action,
    ActionList,
    BBoxGeometry,
    Condition,
    Detector,
    DetectorGroup,
    EdgeModelInfo,
    ModeEnum,
    PaginatedRuleList,
    PayloadTemplate,
    Rule,
    WebhookAction,
)
from urllib3.response import HTTPResponse

from groundlight.images import parse_supported_image_types
from groundlight.internalapi import _generate_request_id
from groundlight.optional_imports import Image, np

from .client import DEFAULT_REQUEST_TIMEOUT, Groundlight, GroundlightClientError, logger


class ExperimentalApi(Groundlight):  # pylint: disable=too-many-public-methods
    def __init__(
        self,
        endpoint: Union[str, None] = None,
        api_token: Union[str, None] = None,
        disable_tls_verification: Optional[bool] = None,
    ):
        """
        Constructs an experimental Groundlight client.

        This client extends the base Groundlight client with additional experimental functionality that is still in
        development. Note that experimental features may undergo significant changes or be removed in future releases.

        **Example usage**::

            from groundlight import ExperimentalApi

            # Create an experimental API client
            gl = ExperimentalApi()

            # Create a notification rule
            rule = gl.create_rule(
                detector="door_detector",
                rule_name="Door Open Alert",
                channel="EMAIL",
                recipient="alerts@company.com",
                alert_on="CHANGED_TO",
                include_image=True,
                condition_parameters={"label": "YES"}
            )

            # Create a detector group
            group = gl.create_detector_group(
                name="Security Detectors",
                description="Detectors monitoring security-related conditions",
                detectors=["door_detector", "motion_detector"]
            )

        :param endpoint: Optional custom API endpoint URL. If not specified, uses the default Groundlight endpoint.
        :param api_token: Authentication token for API access. If not provided, will attempt to read from
                the "GROUNDLIGHT_API_TOKEN" environment variable.
        :param disable_tls_verification: If True, disables SSL/TLS certificate verification for API calls.
                When not specified, checks the "DISABLE_TLS_VERIFY" environment variable (1=disable, 0=enable).
                Certificate verification is enabled by default.

                Warning: Only disable verification when connecting to a Groundlight Edge Endpoint using
                self-signed certificates. For security, always keep verification enabled when using the
                Groundlight cloud service.
        """
        super().__init__(endpoint=endpoint, api_token=api_token, disable_tls_verification=disable_tls_verification)
        self.actions_api = ActionsApi(self.api_client)
        self.images_api = ImageQueriesApi(self.api_client)
        self.notes_api = NotesApi(self.api_client)
        self.detector_group_api = DetectorGroupsApi(self.api_client)
        self.detector_reset_api = DetectorResetApi(self.api_client)

        self.edge_api = EdgeApi(self.api_client)

    ITEMS_PER_PAGE = 100

    def make_condition(self, verb: str, parameters: dict) -> Condition:
        """
        Creates a Condition object for use in creating alerts

        This function serves as a convenience method; Condition objects can also be created directly.

        **Example usage**::

            gl = ExperimentalApi()

            # Create a condition for a rule
            condition = gl.make_condition("CHANGED_TO", {"label": "YES"})

        :param verb: The condition verb to use. One of "ANSWERED_CONSECUTIVELY", "ANSWERED_WITHIN_TIME",
                    "CHANGED_TO", "NO_CHANGE", "NO_QUERIES"
        :param condition_parameters: Additional parameters for the condition, dependant on the verb:
            - For ANSWERED_CONSECUTIVELY: {"num_consecutive_labels": N, "label": "YES/NO"}
            - For CHANGED_TO: {"label": "YES/NO"}
            - For ANSWERED_WITHIN_TIME: {"time_value": N, "time_unit": "MINUTES/HOURS/DAYS"}

        :return: The created Condition object
        """
        return Condition(verb=verb, parameters=parameters)

    def make_action(
        self,
        channel: str,
        recipient: str,
        include_image: bool,
    ) -> Action:
        """
        Creates an Action object for use in creating alerts

        This function serves as a convenience method; Action objects can also be created directly.

        **Example usage**::

            gl = ExperimentalApi()

            # Create an action for an alert
            action = gl.make_action("EMAIL", "example@example.com", include_image=True)

        :param channel: The notification channel to use. One of "EMAIL" or "TEXT"
        :param recipient: The email address or phone number to send notifications to
        :param include_image: Whether to include the triggering image in action message
        """
        return Action(
            channel=channel,
            recipient=recipient,
            include_image=include_image,
        )

    def make_webhook_action(
        self, url: str, include_image: bool, payload_template: Optional[PayloadTemplate] = None
    ) -> WebhookAction:
        """
        Creates a WebhookAction object for use in creating alerts
        This function serves as a convenience method; WebhookAction objects can also be created directly.
        **Example usage**::
            gl = ExperimentalApi()
            # Create a webhook action for an alert
            action = gl.make_webhook_action("https://example.com/webhook", include_image=True)
        :param url: The URL to send the webhook to
        :param include_image: Whether to include the triggering image in the webhook payload
        :param payload_template: Optional custom template for the webhook payload. The template will be rendered with
            the alert data. The template must be a valid Jinja2 template which produces valid JSON when rendered. If no
            template is provided, the default template designed for Slack will be used.
        """
        return WebhookAction(
            url=str(url),
            include_image=include_image,
            payload_template=payload_template,
        )

    def make_payload_template(self, template: str, headers: Optional[Dict[str, str]] = None) -> PayloadTemplate:
        """
        Creates a PayloadTemplate object for use in creating alerts
        """
        return PayloadTemplate(template=template, headers=headers)

    def create_alert(  # pylint: disable=too-many-locals, too-many-arguments  # noqa: PLR0913
        self,
        detector: Union[str, Detector],
        name,
        condition: Condition,
        actions: Optional[Union[Action, List[Action], ActionList]] = None,
        webhook_actions: Optional[Union[WebhookAction, List[WebhookAction]]] = None,
        *,
        enabled: bool = True,
        snooze_time_enabled: bool = False,
        snooze_time_value: int = 3600,
        snooze_time_unit: str = "SECONDS",
        human_review_required: bool = False,
    ) -> Rule:
        """
        Creates an alert for a detector that will trigger actions based on specified conditions.

        An alert allows you to configure automated actions when certain conditions are met,
        such as when a detector's prediction changes or maintains a particular state.

        .. note::
            Currently, only binary mode detectors (YES/NO answers) are supported for alerts.

        **Example usage**::

            gl = ExperimentalApi()

            # Create a rule to send email alerts when door is detected as open
            condition = gl.make_condition(
                verb="CHANGED_TO",
                parameters={"label": "YES"}
            )
            action1 = gl.make_action(
                "EMAIL",
                "alerts@company.com",
                include_image=True
            )
            action2 = gl.make_action(
                "TEXT",
                "+1234567890",
                include_image=False
            )
            alert = gl.create_alert(
                detector="det_idhere",
                name="Door Open Alert",
                condition=condition,
                actions=[action1, action2]
            )

        :param detector: The detector ID or Detector object to add the alert to
        :param name: A unique name to identify this alert
        :param condition: The condition to use for the alert
        :param actions: The actions to use for the alert. Optional if webhook_actions are provided (default None)
        :param webhook_actions: The webhook actions to use for the alert. Optional if actions are provided (default
            None)
        :param enabled: Whether the alert should be active when created (default True)
        :param snooze_time_enabled: Enable notification snoozing to prevent alert spam (default False)
        :param snooze_time_value: Duration of snooze period (default 3600)
        :param snooze_time_unit: Unit for snooze duration - "SECONDS", "MINUTES", "HOURS", or "DAYS" (default "SECONDS")
        :param human_review_required: Require human verification before sending alerts (default False)

        :return: The created Alert object
        """
        if isinstance(actions, Action):
            actions = [actions]
        elif isinstance(actions, ActionList):
            actions = actions.root
        if isinstance(detector, Detector):
            detector = detector.id
        if isinstance(webhook_actions, WebhookAction):
            webhook_actions = [webhook_actions]
        # translate pydantic type to the openapi type
        actions = (
            [
                ActionRequest(
                    channel=ChannelEnum(action.channel), recipient=action.recipient, include_image=action.include_image
                )
                for action in actions
            ]
            if actions
            else []
        )
        webhook_actions = (
            [
                WebhookActionRequest(
                    url=str(webhook_action.url),
                    include_image=webhook_action.include_image,
                    payload_template=(
                        PayloadTemplateRequest(
                            template=webhook_action.payload_template.template,
                            headers=webhook_action.payload_template.headers,
                        )
                        if webhook_action.payload_template
                        else None
                    ),
                )
                for webhook_action in webhook_actions
            ]
            if webhook_actions
            else []
        )
        rule_input = RuleRequest(
            detector_id=detector,
            name=name,
            enabled=enabled,
            action=actions,
            condition=ConditionRequest(verb=condition.verb, parameters=condition.parameters),
            snooze_time_enabled=snooze_time_enabled,
            snooze_time_value=snooze_time_value,
            snooze_time_unit=snooze_time_unit,
            human_review_required=human_review_required,
            webhook_action=webhook_actions,
        )
        return Rule.model_validate(self.actions_api.create_rule(detector, rule_input).to_dict())

    def create_rule(  # pylint: disable=too-many-locals  # noqa: PLR0913
        self,
        detector: Union[str, Detector],
        rule_name: str,
        channel: Union[str, ChannelEnum],
        recipient: str,
        *,
        alert_on: str = "CHANGED_TO",
        enabled: bool = True,
        include_image: bool = False,
        condition_parameters: Union[str, dict, None] = None,
        snooze_time_enabled: bool = False,
        snooze_time_value: int = 3600,
        snooze_time_unit: str = "SECONDS",
        human_review_required: bool = False,
    ) -> Rule:
        """
        DEPRECATED: Use create_alert instead.

        Creates a notification rule for a detector that will send alerts based on specified conditions.

        A notification rule allows you to configure automated alerts when certain conditions are met,
        such as when a detector's prediction changes or maintains a particular state.

        .. note::
            Currently, only binary mode detectors (YES/NO answers) are supported for notification rules.

        **Example usage**::

            gl = ExperimentalApi()

            # Create a rule to send email alerts when door is detected as open
            rule = gl.create_rule(
                detector="door_detector",
                rule_name="Door Open Alert",
                channel="EMAIL",
                recipient="alerts@company.com",
                alert_on="CHANGED_TO",
                condition_parameters={"label": "YES"},
                include_image=True
            )

            # Create a rule for consecutive motion detections via SMS
            rule = gl.create_rule(
                detector="motion_detector",
                rule_name="Repeated Motion Alert",
                channel="TEXT",
                recipient="+1234567890",
                alert_on="ANSWERED_CONSECUTIVELY",
                condition_parameters={
                    "num_consecutive_labels": 3,
                    "label": "YES"
                },
                snooze_time_enabled=True,
                snooze_time_value=1,
                snooze_time_unit="HOURS"
            )

        :param detector: The detector ID or Detector object to add the rule to
        :param rule_name: A unique name to identify this rule
        :param channel: Notification channel - either "EMAIL" or "TEXT"
        :param recipient: Email address or phone number to receive notifications
        :param alert_on: what to alert on. One of ANSWERED_CONSECUTIVELY, ANSWERED_WITHIN_TIME,
            CHANGED_TO, NO_CHANGE, NO_QUERIES
        :param enabled: Whether the rule should be active when created (default True)
        :param include_image: Whether to attach the triggering image to notifications (default False)
        :param condition_parameters: Additional parameters for the alert condition:
            - For ANSWERED_CONSECUTIVELY: {"num_consecutive_labels": N, "label": "YES/NO"}
            - For CHANGED_TO: {"label": "YES/NO"}
            - For time-based conditions: {"time_value": N, "time_unit": "MINUTES/HOURS/DAYS"}
        :param snooze_time_enabled: Enable notification snoozing to prevent alert spam (default False)
        :param snooze_time_value: Duration of snooze period (default 3600)
        :param snooze_time_unit: Unit for snooze duration - "SECONDS", "MINUTES", "HOURS", or "DAYS" (default "SECONDS")
        :param human_review_required: Require human verification before sending alerts (default False)

        :return: The created Rule object
        """

        logger.warning("create_rule is no longer supported. Please use create_alert instead.")

        if condition_parameters is None:
            condition_parameters = {}
        if isinstance(channel, str):
            channel = ChannelEnum(channel.upper())
        if isinstance(condition_parameters, str):
            condition_parameters = json.loads(condition_parameters)  # type: ignore
        action = ActionRequest(
            channel=channel,  # type: ignore
            recipient=recipient,
            include_image=include_image,
        )
        condition = ConditionRequest(verb=alert_on, parameters=condition_parameters)  # type: ignore
        det_id = detector.id if isinstance(detector, Detector) else detector
        rule_input = RuleRequest(
            detector_id=det_id,
            name=rule_name,
            enabled=enabled,
            action=action,
            condition=condition,
            snooze_time_enabled=snooze_time_enabled,
            snooze_time_value=snooze_time_value,
            snooze_time_unit=snooze_time_unit,
            human_review_required=human_review_required,
        )
        return Rule.model_validate(self.actions_api.create_rule(det_id, rule_input).to_dict())

    def get_rule(self, action_id: int) -> Rule:
        """
        Gets the rule with the given id.

        **Example usage**::

            gl = ExperimentalApi()

            # Get an existing rule by ID
            rule = gl.get_rule(action_id=123)
            print(f"Rule name: {rule.name}")
            print(f"Rule enabled: {rule.enabled}")

        :param action_id: the id of the rule to get
        :return: the Rule object with the given id
        """
        return Rule.model_validate(self.actions_api.get_rule(action_id).to_dict())

    def delete_rule(self, action_id: int) -> None:
        """
        Deletes the rule with the given id.

        **Example usage**::

            gl = ExperimentalApi()

            # Delete a specific rule
            gl.delete_rule(action_id=123)

        :param action_id: the id of the rule to delete
        """
        self.actions_api.delete_rule(action_id)

    def list_rules(self, page=1, page_size=10) -> PaginatedRuleList:
        """
        Gets a paginated list of all rules.

        **Example usage**::

            gl = ExperimentalApi()

            # Get first page of rules
            rules = gl.list_rules(page=1, page_size=10)
            print(f"Total rules: {rules.count}")

            # Iterate through rules on current page
            for rule in rules.results:
                print(f"Rule {rule.id}: {rule.name}")

            # Get next page
            next_page = gl.list_rules(page=2, page_size=10)

        :param page: Page number to retrieve (default: 1)
        :param page_size: Number of rules per page (default: 10)
        :return: PaginatedRuleList containing the rules and pagination info
        """
        obj = self.actions_api.list_rules(page=page, page_size=page_size)
        return PaginatedRuleList.parse_obj(obj.to_dict())

    def delete_all_rules(self, detector: Union[None, str, Detector] = None) -> int:
        """
        Deletes all rules associated with the given detector. If no detector is specified,
        deletes all rules in the account.

        WARNING: If no detector is specified, this will delete ALL rules in your account.
        This action cannot be undone. Use with caution.

        **Example usage**::

            gl = ExperimentalApi()

            # Delete all rules for a specific detector
            detector = gl.get_detector("my_detector")
            num_deleted = gl.delete_all_rules(detector)
            print(f"Deleted {num_deleted} rules")

            # Delete all rules in the account
            num_deleted = gl.delete_all_rules()
            print(f"Deleted {num_deleted} rules")

        :param detector: the detector to delete the rules from. If None, deletes all rules.

        :return: the number of rules deleted
        """
        det_id = detector.id if isinstance(detector, Detector) else detector
        # we collect a list of all the rules to delete, then delete them
        ids_to_delete = []
        num_rules = self.list_rules().count
        for page in range(1, (num_rules // self.ITEMS_PER_PAGE) + 2):
            for rule in self.list_rules(page=page, page_size=self.ITEMS_PER_PAGE).results:
                if det_id is None:
                    ids_to_delete.append(rule.id)
                elif rule.detector_id == det_id:
                    ids_to_delete.append(rule.id)
        for rule_id in ids_to_delete:
            self.delete_rule(rule_id)
        return num_rules

    def get_image(self, iq_id: str) -> bytes:
        """
        Get the image associated with the given image query ID.

        **Example usage**::

            gl = ExperimentalApi()

            # Get image from an image query
            iq = gl.get_image_query("iq_123")
            image_bytes = gl.get_image(iq.id)

            # Open with PIL - returns RGB order
            from PIL import Image
            image = Image.open(gl.get_image(iq.id))  # Returns RGB image

            # Open with numpy via PIL - returns RGB order
            import numpy as np
            from io import BytesIO
            image = np.array(Image.open(gl.get_image(iq.id)))  # Returns RGB array

            # Open with OpenCV - returns BGR order
            import cv2
            import numpy as np
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # Returns BGR array
            # To convert to RGB if needed:
            # image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        :param iq_id: The ID of the image query to get the image from
        :return: The image as a byte array that can be used with PIL or other image libraries
        """
        # TODO: support taking an ImageQuery object
        return self.images_api.get_image(iq_id)

    def get_notes(self, detector: Union[str, Detector]) -> Dict[str, Any]:
        """
        Retrieves all notes associated with a detector.

        **Example usage**::

            gl = ExperimentalApi()

            detector = gl.get_detector("det_123")
            notes = gl.get_notes(detector)
            # notes = {
            #     "CUSTOMER": ["Customer note 1", "Customer note 2"],
            #     "GL": ["Groundlight note 1"]
            # }

        :param detector: The detector object or ID string to retrieve notes for

        :return: A dictionary containing notes organized by source ("CUSTOMER" or "GL"),
            where each source maps to a list of note strings
        """
        det_id = detector.id if isinstance(detector, Detector) else detector
        return self.notes_api.get_notes(det_id)

    def create_note(
        self,
        detector: Union[str, Detector],
        note: str,
        image: Union[str, bytes, Image.Image, BytesIO, BufferedReader, np.ndarray, None] = None,
    ) -> None:
        """
        Adds a note to a given detector.

        **Example usage**::

            gl = ExperimentalApi()

            detector = gl.get_detector("det_123")
            gl.create_note(detector, "Please label doors that are slightly ajar as 'YES'")

            # With an image attachment
            gl.create_note(
                detector,
                "Door that is slightly ajar and should be labeled 'YES'",
                image="path/to/image.jpg"
            )

        :param detector: The detector object or detector ID string to add the note to
        :param note: The text content of the note to add
        :param image: Optional image to attach to the note.
        """
        det_id = detector.id if isinstance(detector, Detector) else detector

        # Initialize img_bytes to None
        img_bytes = None
        if image is not None:
            img_bytes = parse_supported_image_types(image)

        # TODO: The openapi generator doesn't handle file submissions well at the moment, so we manually implement this
        # kwargs = {"image": img_bytes}
        # self.notes_api.create_note(det_id, note, **kwargs)
        url = f"{self.endpoint}/v1/notes"
        files = {"image": ("image.jpg", img_bytes, "image/jpeg")} if img_bytes is not None else None
        data = {"content": note}
        params = {"detector_id": det_id}
        headers = {"x-api-token": self.configuration.api_key["ApiToken"]}

        response = requests.post(url, headers=headers, data=data, files=files, params=params)  # type: ignore
        response.raise_for_status()  # Raise an exception for error status codes

    def create_detector_group(self, name: str) -> DetectorGroup:
        """
        Creates a detector group with the given name. A detector group allows you to organize
        related detectors together.

        .. note::
            You can specify a detector group when creating a detector without the need to create it ahead of time.
            The group will be created automatically if it doesn't exist.

        **Example usage**::

            gl = ExperimentalApi()

            # Create a group for all door-related detectors
            door_group = gl.create_detector_group("door-detectors")

            # Later, create detectors in this group
            door_open_detector = gl.create_detector(
                name="front-door-open",
                query="Is the front door open?",
                detector_group=door_group
            )

        :param name: The name of the detector group. This should be descriptive and unique within your organization.
        :type name: str
        :return: A DetectorGroup object corresponding to the newly created detector group
        :rtype: DetectorGroup
        """
        return DetectorGroup(**self.detector_group_api.create_detector_group(DetectorGroupRequest(name=name)).to_dict())

    def list_detector_groups(self) -> List[DetectorGroup]:
        """
        Gets a list of all detector groups in your account.

        **Example usage**::

            gl = ExperimentalApi()

            # Get all detector groups
            groups = gl.list_detector_groups()

            # Print information about each group
            for group in groups:
                print(f"Group name: {group.name}")
                print(f"Group ID: {group.id}")

        :return: A list of DetectorGroup objects representing all detector groups in your account
        """
        return [DetectorGroup(**det.to_dict()) for det in self.detector_group_api.get_detector_groups()]

    def create_roi(self, label: str, top_left: Tuple[float, float], bottom_right: Tuple[float, float]) -> ROI:
        """
        Creates a Region of Interest (ROI) object that can be used to specify areas of interest in images. Certain
        detectors (such as Count-mode detectors) may emit ROIs as part of their output. Providing an ROI can help
        improve the accuracy of such detectors.

        .. note::
            ROI functionality is only available to Pro tier and higher.
            If you would like to learn more, reach out to us at https://groundlight.ai

        **Example usage**::

            gl = ExperimentalApi()

            # Create an ROI for a door in the image
            door_roi = gl.create_roi(
                label="door",
                top_left=(0.2, 0.3),     # Coordinates are normalized (0-1)
                bottom_right=(0.4, 0.8)  # Coordinates are normalized (0-1)
            )

            # Use the ROI when submitting an image query
            query = gl.submit_image_query(
                detector="door-detector",
                image=image_bytes,
                rois=[door_roi]
            )

        :param label: A descriptive label for the object or area contained in the ROI
        :param top_left: Tuple of (x, y) coordinates for the top-left corner, normalized to [0,1]
        :param bottom_right: Tuple of (x, y) coordinates for the bottom-right corner, normalized to [0,1]
        :return: An ROI object that can be used in image queries
        """

        return ROI(
            label=label,
            score=1.0,
            geometry=BBoxGeometry(
                left=top_left[0],
                top=top_left[1],
                right=bottom_right[0],
                bottom=bottom_right[1],
                x=(top_left[0] + bottom_right[0]) / 2,
                y=(top_left[1] + bottom_right[1]) / 2,
            ),
        )

    def reset_detector(self, detector: Union[str, Detector]) -> None:
        """
        Removes all image queries and training data for the given detector. This effectively resets
        the detector to its initial state, allowing you to start fresh with new training data.

        .. warning::
            This operation cannot be undone. All image queries and training data will be deleted.

        **Example usage**::

            gl = ExperimentalApi()

            # Using a detector object
            detector = gl.get_detector("det_abc123")
            gl.reset_detector(detector)

            # Using a detector ID string directly
            gl.reset_detector("det_abc123")

        :param detector: Either a Detector object or a detector ID string starting with "det_".
                       The detector whose data should be reset.

        :return: None
        """
        if isinstance(detector, Detector):
            detector = detector.id
        self.detector_reset_api.reset_detector(detector)

    def update_detector_name(self, detector: Union[str, Detector], name: str) -> None:
        """
        Updates the name of the given detector

        **Example usage**::

            gl = ExperimentalApi()

            # Using a detector object
            detector = gl.get_detector("det_abc123")
            gl.update_detector_name(detector, "new_detector_name")

            # Using a detector ID string directly
            gl.update_detector_name("det_abc123", "new_detector_name")

        :param detector: Either a Detector object or a detector ID string starting with "det_".
                       The detector whose name should be updated.
        :param name: The new name to assign to the detector

        :return: None
        """
        if isinstance(detector, Detector):
            detector = detector.id
        self.detectors_api.update_detector(detector, patched_detector_request=PatchedDetectorRequest(name=name))

    def update_detector_status(self, detector: Union[str, Detector], enabled: bool) -> None:
        """
        Updates the status of the given detector. When a detector is disabled (enabled=False),
        it will not accept or process any new image queries. Existing queries will not be affected.

        **Example usage**::

            gl = ExperimentalApi()

            # Using a detector object
            detector = gl.get_detector("det_abc123")
            gl.update_detector_status(detector, enabled=False)  # Disable the detector

            # Using a detector ID string directly
            gl.update_detector_status("det_abc123", enabled=True)  # Enable the detector

        :param detector: Either a Detector object or a detector ID string starting with "det_".
                       The detector whose status should be updated.
        :param enabled: Boolean indicating whether the detector should be enabled (True) or
                       disabled (False). When disabled, the detector will not process new queries.

        :return: None
        """
        if isinstance(detector, Detector):
            detector = detector.id
        self.detectors_api.update_detector(
            detector,
            patched_detector_request=PatchedDetectorRequest(status=StatusEnum("ON") if enabled else StatusEnum("OFF")),
        )

    def update_detector_escalation_type(self, detector: Union[str, Detector], escalation_type: str) -> None:
        """
        Updates the escalation type of the given detector, controlling whether queries can be
        sent to human labelers when ML confidence is low.

        This is particularly useful for controlling costs. When set to "NO_HUMAN_LABELING",
        queries will only receive ML predictions, even if confidence is low.
        When set to "STANDARD", low-confidence queries may be sent to human labelers for verification.

        **Example usage**::

            gl = ExperimentalApi()

            # Using a detector object
            detector = gl.get_detector("det_abc123")

            # Disable human labeling
            gl.update_detector_escalation_type(detector, "NO_HUMAN_LABELING")

            # Re-enable standard human labeling
            gl.update_detector_escalation_type("det_abc123", "STANDARD")

        :param detector: Either a Detector object or a detector ID string starting with "det_".
                       The detector whose escalation type should be updated.
        :param escalation_type: The new escalation type setting. Must be one of:
                              - "STANDARD": Allow human labeling for low-confidence queries
                              - "NO_HUMAN_LABELING": Never send queries to human labelers

        :return: None
        :raises ValueError: If escalation_type is not one of the allowed values
        """
        if isinstance(detector, Detector):
            detector = detector.id
        escalation_type = escalation_type.upper()
        if escalation_type not in ["STANDARD", "NO_HUMAN_LABELING"]:
            raise ValueError("escalation_type must be either 'STANDARD' or 'NO_HUMAN_LABELING'")
        self.detectors_api.update_detector(
            detector,
            patched_detector_request=PatchedDetectorRequest(escalation_type=escalation_type),
        )

    def create_counting_detector(  # noqa: PLR0913 # pylint: disable=too-many-arguments, too-many-locals
        self,
        name: str,
        query: str,
        class_name: str,
        *,
        max_count: Optional[int] = None,
        group_name: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
        patience_time: Optional[float] = None,
        pipeline_config: Optional[str] = None,
        metadata: Union[dict, str, None] = None,
    ) -> Detector:
        """
        Creates a counting detector that can count objects in images up to a specified maximum count.

        **Example usage**::

            gl = ExperimentalApi()

            # Create a detector that counts people up to 5
            detector = gl.create_counting_detector(
                name="people_counter",
                query="How many people are in the image?",
                class_name="person",
                max_count=5,
                confidence_threshold=0.9,
                patience_time=30.0
            )

            # Use the detector to count people in an image
            image_query = gl.ask_ml(detector, "path/to/image.jpg")
            print(f"Counted {image_query.result.count} people")
            print(f"Confidence: {image_query.result.confidence}")

        :param name: A short, descriptive name for the detector.
        :param query: A question about the count of an object in the image.
        :param class_name: The class name of the object to count.
        :param max_count: Maximum number of objects to count (default: 10)
        :param group_name: Optional name of a group to organize related detectors together.
        :param confidence_threshold: A value that sets the minimum confidence level required for the ML model's
                            predictions. If confidence is below this threshold, the query may be sent for human review.
        :param patience_time: The maximum time in seconds that Groundlight will attempt to generate a
                            confident prediction before falling back to human review. Defaults to 30 seconds.
        :param pipeline_config: Advanced usage only. Configuration string needed to instantiate a specific
                              prediction pipeline for this detector.
        :param metadata: A dictionary or JSON string containing custom key/value pairs to associate with
                        the detector (limited to 1KB). This metadata can be used to store additional
                        information like location, purpose, or related system IDs. You can retrieve this
                        metadata later by calling `get_detector()`.

        :return: The created Detector object
        """

        detector_creation_input = self._prep_create_detector(
            name=name,
            query=query,
            group_name=group_name,
            confidence_threshold=confidence_threshold,
            patience_time=patience_time,
            pipeline_config=pipeline_config,
            metadata=metadata,
        )
        detector_creation_input.mode = ModeEnum.COUNT

        if max_count is None:
            mode_config = CountModeConfiguration(class_name=class_name)
        else:
            mode_config = CountModeConfiguration(max_count=max_count, class_name=class_name)

        detector_creation_input.mode_configuration = mode_config
        obj = self.detectors_api.create_detector(detector_creation_input, _request_timeout=DEFAULT_REQUEST_TIMEOUT)
        return Detector.parse_obj(obj.to_dict())

    def create_multiclass_detector(  # noqa: PLR0913 # pylint: disable=too-many-arguments, too-many-locals
        self,
        name: str,
        query: str,
        class_names: List[str],
        *,
        group_name: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
        patience_time: Optional[float] = None,
        pipeline_config: Optional[str] = None,
        metadata: Union[dict, str, None] = None,
    ) -> Detector:
        """
        Creates a multiclass detector with the given name and query.

        **Example usage**::

            gl = ExperimentalApi()

            detector = gl.create_multiclass_detector(
                name="Traffic Light Detector",
                query="What color is the traffic light?",
                class_names=["Red", "Yellow", "Green"]
            )

            # Use the detector to classify a traffic light
            image_query = gl.ask_ml(detector, "path/to/image.jpg")
            print(f"Traffic light is {image_query.result.label}")
            print(f"Confidence: {image_query.result.confidence}")

        :param name: A short, descriptive name for the detector.
        :param query: A question about classifying objects in the image.
        :param class_names: List of possible class labels for classification.
        :param group_name: Optional name of a group to organize related detectors together.
        :param confidence_threshold: A value between 1/num_classes and 1 that sets the minimum confidence level required
                                  for the ML model's predictions. If confidence is below this threshold,
                                  the query may be sent for human review.
        :param patience_time: The maximum time in seconds that Groundlight will attempt to generate a
                            confident prediction before falling back to human review. Defaults to 30 seconds.
        :param pipeline_config: Advanced usage only. Configuration string needed to instantiate a specific
                              prediction pipeline for this detector.
        :param metadata: A dictionary or JSON string containing custom key/value pairs to associate with
                        the detector (limited to 1KB). This metadata can be used to store additional
                        information like location, purpose, or related system IDs. You can retrieve this
                        metadata later by calling `get_detector()`.

        :return: The created Detector object
        """

        detector_creation_input = self._prep_create_detector(
            name=name,
            query=query,
            group_name=group_name,
            confidence_threshold=confidence_threshold,
            patience_time=patience_time,
            pipeline_config=pipeline_config,
            metadata=metadata,
        )
        detector_creation_input.mode = ModeEnum.MULTI_CLASS
        mode_config = MultiClassModeConfiguration(class_names=class_names)
        detector_creation_input.mode_configuration = mode_config
        obj = self.detectors_api.create_detector(detector_creation_input, _request_timeout=DEFAULT_REQUEST_TIMEOUT)
        return Detector.parse_obj(obj.to_dict())

    def create_bounding_box_detector(  # noqa: PLR0913 # pylint: disable=too-many-arguments, too-many-locals
        self,
        name: str,
        query: str,
        class_name: str,
        *,
        max_num_bboxes: Optional[int] = None,
        group_name: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
        patience_time: Optional[float] = None,
        pipeline_config: Optional[str] = None,
        metadata: Union[dict, str, None] = None,
    ) -> Detector:
        """
        Creates a bounding box detector that can detect objects in images up to a specified maximum number of bounding
        boxes.

        **Example usage**::

            gl = ExperimentalApi()

            # Create a detector that counts people up to 5
            detector = gl.create_bounding_box_detector(
                name="people_counter",
                query="Draw a bounding box around each person in the image",
                class_name="person",
                max_num_bboxes=5,
                confidence_threshold=0.9,
                patience_time=30.0
            )

            # Use the detector to find people in an image
            image_query = gl.ask_ml(detector, "path/to/image.jpg")
            print(f"Confidence: {image_query.result.confidence}")
            print(f"Bounding boxes: {image_query.result.rois}")

        :param name: A short, descriptive name for the detector.
        :param query: A question about the object to detect in the image.
        :param class_name: The class name of the object to detect.
        :param max_num_bboxes: Maximum number of bounding boxes to detect (default: 10)
        :param group_name: Optional name of a group to organize related detectors together.
        :param confidence_threshold: A value that sets the minimum confidence level required for the ML model's
                            predictions. If confidence is below this threshold, the query may be sent for human review.
        :param patience_time: The maximum time in seconds that Groundlight will attempt to generate a
                            confident prediction before falling back to human review. Defaults to 30 seconds.
        :param pipeline_config: Advanced usage only. Configuration string needed to instantiate a specific
                              prediction pipeline for this detector.
        :param metadata: A dictionary or JSON string containing custom key/value pairs to associate with
                        the detector (limited to 1KB). This metadata can be used to store additional
                        information like location, purpose, or related system IDs. You can retrieve this
                        metadata later by calling `get_detector()`.

        :return: The created Detector object
        """

        detector_creation_input = self._prep_create_detector(
            name=name,
            query=query,
            group_name=group_name,
            confidence_threshold=confidence_threshold,
            patience_time=patience_time,
            pipeline_config=pipeline_config,
            metadata=metadata,
        )
        detector_creation_input.mode = ModeEnum.BOUNDING_BOX

        if max_num_bboxes is None:
            mode_config = BoundingBoxModeConfiguration(class_name=class_name)
        else:
            mode_config = BoundingBoxModeConfiguration(max_num_bboxes=max_num_bboxes, class_name=class_name)

        detector_creation_input.mode_configuration = mode_config
        obj = self.detectors_api.create_detector(detector_creation_input, _request_timeout=DEFAULT_REQUEST_TIMEOUT)
        return Detector.parse_obj(obj.to_dict())

    def _download_mlbinary_url(self, detector: Union[str, Detector]) -> EdgeModelInfo:
        """
        Gets a temporary presigned URL to download the model binaries for the given detector, along
        with relevant metadata
        """
        if isinstance(detector, Detector):
            detector = detector.id
        obj = self.edge_api.get_model_urls(detector)
        return EdgeModelInfo.parse_obj(obj.to_dict())

    def download_mlbinary(self, detector: Union[str, Detector], output_dir: str) -> None:
        """
        Downloads the model binary files for the given detector to the specified output path.

        **Example usage**::

            gl = ExperimentalApi()

            # Download the model binary for a detector
            detector = gl.get_detector("det_abc123")
            gl.download_mlbinary(detector, "path/to/output/model.bin")

        :param detector: The detector object or detector ID string to download the model binary for.
        :param output_path: The path to save the model binary file to.

        :return: None
        """

        def _download_and_save(url: str, output_path: str) -> bytes:
            try:
                response = requests.get(url, timeout=10)
            except Exception as e:
                raise GroundlightClientError(f"Failed to retrieve data from {url}.") from e
            with open(output_path, "wb") as file:
                file.write(response.content)
            return response.content

        if isinstance(detector, Detector):
            detector = detector.id
        edge_model_info = self._download_mlbinary_url(detector)
        _download_and_save(edge_model_info.model_binary_url, Path(output_dir) / edge_model_info.model_binary_id)
        _download_and_save(
            edge_model_info.oodd_model_binary_url, Path(output_dir) / edge_model_info.oodd_model_binary_id
        )

    def get_detector_evaluation(self, detector: Union[str, Detector]) -> dict:
        """
        Get a specific evaluation for a detector

        :param detector: the detector to get the evaluation for

        :return: a dictionary containing the evaluation results
        """
        if isinstance(detector, Detector):
            detector = detector.id
        obj = self.detectors_api.get_detector_evaluation(detector)
        return obj.to_dict()

    def get_detector_metrics(self, detector: Union[str, Detector]) -> dict:
        """
        Get the metrics for a detector

        :param detector: the detector to get the metrics for

        :return: a dictionary containing the metrics for the detector
        """
        if isinstance(detector, Detector):
            detector = detector.id
        obj = self.detectors_api.get_detector_metrics(detector)
        return obj.to_dict()

    def get_raw_headers(self) -> dict:
        """
        Get the raw headers for the current API client

        :return: a dictionary containing the raw headers
        """
        headers = {}
        # see generated/groundlight_openapi_client/api_client.py update_params_for_auth
        headers["x-api-token"] = self.api_client.configuration.api_key["ApiToken"]
        # We generate a unique request ID client-side for each request
        headers["X-Request-Id"] = _generate_request_id()
        headers["User-Agent"] = self.api_client.default_headers["User-Agent"]
        headers["Accept"] = "application/json"
        return headers

    def make_generic_api_request(  # noqa: PLR0913 # pylint: disable=too-many-arguments
        self,
        *,
        endpoint: str,
        method: str,
        headers: Union[dict, None] = None,
        body: Union[dict, None] = None,
        files=None,
    ) -> HTTPResponse:
        """
        Make a generic API request to the specified endpoint, utilizing many of the provided tools
        from the generated api client

        :param endpoint: the endpoint to send the request to - the url path appended after the
            endpoint including a / at the beginging
        :param method: the HTTP method to use
        :param body: the request body

        :return: a dictionary containing the response
        """
        # HEADERS MUST BE THE 4TH ARGUMENT, 0 INDEXED
        if not headers:
            headers = self.get_raw_headers()
        return self.api_client.call_api(
            endpoint,
            method,
            None,  # Path Params
            None,  # Query params
            headers,  # header params
            body=body,  # body
            files=files,  # files
            auth_settings=["ApiToken"],
            _preload_content=False,  # This returns the urllib3 response rather than trying any type of processing
        )
