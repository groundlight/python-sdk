"""
experimental_api.py

This module is part of our evolving SDK. While these functions are designed to provide valuable functionality to enhance
your projects, it's important to note that they are considered unstable. This means they may undergo significant
modifications or potentially be removed in future releases, which could lead to breaking changes in your applications.
"""
import json
from typing import Any, Dict, Union

from groundlight_openapi_client.api.images_api import ImagesApi
from groundlight_openapi_client.api.notes_api import NotesApi
from groundlight_openapi_client.api.rules_api import RulesApi
from groundlight_openapi_client.model.action import Action
from groundlight_openapi_client.model.condition import Condition
from groundlight_openapi_client.model.note_creation_input import NoteCreationInput
from groundlight_openapi_client.model.rule_creation_input import RuleCreationInput
from model import Channel, Detector, PaginatedRuleList, Rule, Verb

from .client import Groundlight


class ExperimentalApi(Groundlight):
    def __init__(self, endpoint: Union[str, None] = None, api_token: Union[str, None] = None):
        super().__init__(endpoint=endpoint, api_token=api_token)
        self.rules_api = RulesApi(self.api_client)
        self.images_api = ImagesApi(self.api_client)
        self.notes_api = NotesApi(self.api_client)

    ITEMS_PER_PAGE = 100

    def create_rule(  # pylint: disable=too-many-locals
        self,
        detector: Union[str, Detector],
        rule_name: str,
        channel: Union[str, Channel],
        recipient: str,
        *,
        alert_on: Union[str, Verb] = "CHANGED_TO",
        enabled: bool = True,
        include_image: bool = False,
        condition_parameters: Union[str, dict, None] = None,
        snooze_time_enabled: bool = False,
        snooze_time_value: int = 3600,
        snooze_time_unit: str = "SECONDS",
    ) -> Rule:
        """
        Adds a notification rule to the given detector

        :param detector: the detector to add the action to
        :param rule_name: a name to uniquely identify the rule
        :param channel: what channel to send the notification over. Currently EMAIL or TEXT
        :param recipient: the address or number to send the notification to
        :param alert_on: what to alert on. One of ANSWERED_CONSECUTIVELY, ANSWERED_WITHIN_TIME,
            CHANGED_TO, NO_CHANGE, NO_QUERIES
        :param enabled: whether the rule is enabled initially
        :param include_image: whether to include the image in the notification
        :param condition_parameters: additional information needed for the condition. i.e. if the
            condition is ANSWERED_CONSECUTIVELY, we specify num_consecutive_labels and label here
        :param snooze_time_enabled: Whether notifications wil be snoozed, no repeat notification
            will be delivered until the snooze time has passed
        :param snooze_time_value: The value of the snooze time
        :param snooze_time_unit: The unit of the snooze time

        :return: a Rule object corresponding to the new rule
        """
        if condition_parameters is None:
            condition_parameters = {}
        if isinstance(alert_on, str):
            alert_on = Verb(alert_on.upper())
        if isinstance(channel, str):
            channel = Channel(channel.upper())
        if isinstance(condition_parameters, str):
            condition_parameters = json.loads(condition_parameters)  # type: ignore
        action = Action(
            channel=channel.value,  # type: ignore
            recipient=recipient,
            include_image=include_image,
        )
        condition = Condition(verb=alert_on.value, parameters=condition_parameters)  # type: ignore
        det_id = detector.id if isinstance(detector, Detector) else detector
        rule_input = RuleCreationInput(
            detector_id=det_id,
            name=rule_name,
            enabled=enabled,
            action=action,
            condition=condition,
            snooze_time_enabled=snooze_time_enabled,
            snooze_time_value=snooze_time_value,
            snooze_time_unit=snooze_time_unit,
        )
        return Rule.model_validate(self.rules_api.create_rule(det_id, rule_input).to_dict())

    def get_rule(self, action_id: int) -> Action:
        """
        Gets the action with the given id

        :param action_id: the id of the action to get
        :return: the action with the given id
        """
        return Rule.model_validate(self.rules_api.get_rule(action_id).to_dict())

    def delete_rule(self, action_id: int) -> None:
        """
        Deletes the action with the given id

        :param action_id: the id of the action to delete
        """
        self.rules_api.delete_rule(action_id)

    def list_rules(self, page=1, page_size=10) -> PaginatedRuleList:
        """
        Gets a list of all rules

        :return: a list of all rules
        """
        obj = self.rules_api.list_rules(page=page, page_size=page_size)
        return PaginatedRuleList.parse_obj(obj.to_dict())

    def delete_all_rules(self, detector: Union[None, str, Detector] = None) -> int:
        """
        Deletes all rules associated with the given detector

        :param detector: the detector to delete the rules from

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
        Get the image associated with the given image ID
        If you have PIL installed, you can instantiate the pill image as PIL.Image.open(gl.get_image(iq.id))

        :param image_id: the ID of the image to get
        :return: the image as a byte array
        """
        return self.images_api.get_image(iq_id)

    def get_notes(self, detector: Union[str, Detector]) -> Dict[str, Any]:
        """
        Gets the notes for a given detector

        :param detector: the detector to get the notes for

        :return: a dictionary with two keys "CUSTOMER" and "GL" to indicate who added the note to
            the detector, and values that are lists of notes
        """
        det_id = detector.id if isinstance(detector, Detector) else detector
        return self.notes_api.get_notes(det_id)

    def create_note(self, detector: Union[str, Detector], note: Union[str, NoteCreationInput]) -> None:
        """
        Adds a note to a given detector

        :param detector: the detector to add the note to
        """
        det_id = detector.id if isinstance(detector, Detector) else detector
        if isinstance(note, str):
            note = NoteCreationInput(content=note)
        self.notes_api.create_note(det_id, note)
