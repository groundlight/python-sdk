"""
    Groundlight API

    Groundlight makes it simple to understand images. You can easily create computer vision detectors just by describing what you want to know using natural language.  # noqa: E501

    The version of the OpenAPI document: 0.18.2
    Contact: support@groundlight.ai
    Generated by: https://openapi-generator.tech
"""

import re  # noqa: F401
import sys  # noqa: F401

from groundlight_openapi_client.api_client import ApiClient, Endpoint as _Endpoint
from groundlight_openapi_client.model_utils import (  # noqa: F401
    check_allowed_values,
    check_validations,
    date,
    datetime,
    file_type,
    none_type,
    validate_and_convert_types,
)
from groundlight_openapi_client.model.all_notes import AllNotes
from groundlight_openapi_client.model.note_request import NoteRequest


class NotesApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client
        self.create_note_endpoint = _Endpoint(
            settings={
                "response_type": None,
                "auth": ["ApiToken"],
                "endpoint_path": "/v1/notes",
                "operation_id": "create_note",
                "http_method": "POST",
                "servers": None,
            },
            params_map={
                "all": [
                    "detector_id",
                    "note_request",
                ],
                "required": [
                    "detector_id",
                ],
                "nullable": [],
                "enum": [],
                "validation": [],
            },
            root_map={
                "validations": {},
                "allowed_values": {},
                "openapi_types": {
                    "detector_id": (str,),
                    "note_request": (NoteRequest,),
                },
                "attribute_map": {
                    "detector_id": "detector_id",
                },
                "location_map": {
                    "detector_id": "query",
                    "note_request": "body",
                },
                "collection_format_map": {},
            },
            headers_map={
                "accept": [],
                "content_type": ["application/json", "application/x-www-form-urlencoded", "multipart/form-data"],
            },
            api_client=api_client,
        )
        self.get_notes_endpoint = _Endpoint(
            settings={
                "response_type": (AllNotes,),
                "auth": ["ApiToken"],
                "endpoint_path": "/v1/notes",
                "operation_id": "get_notes",
                "http_method": "GET",
                "servers": None,
            },
            params_map={
                "all": [
                    "detector_id",
                ],
                "required": [
                    "detector_id",
                ],
                "nullable": [],
                "enum": [],
                "validation": [],
            },
            root_map={
                "validations": {},
                "allowed_values": {},
                "openapi_types": {
                    "detector_id": (str,),
                },
                "attribute_map": {
                    "detector_id": "detector_id",
                },
                "location_map": {
                    "detector_id": "query",
                },
                "collection_format_map": {},
            },
            headers_map={
                "accept": ["application/json"],
                "content_type": [],
            },
            api_client=api_client,
        )

    def create_note(self, detector_id, **kwargs):
        """create_note  # noqa: E501

        Creates a new note.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.create_note(detector_id, async_req=True)
        >>> result = thread.get()

        Args:
            detector_id (str): the detector to associate the new note with

        Keyword Args:
            note_request (NoteRequest): [optional]
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _spec_property_naming (bool): True if the variable names in the input data
                are serialized names, as specified in the OpenAPI document.
                False if the variable names in the input data
                are pythonic names, e.g. snake case (default)
            _content_type (str/None): force body content-type.
                Default is None and content-type will be predicted by allowed
                content-types and body.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            None
                If the method is called asynchronously, returns the request
                thread.
        """
        kwargs["async_req"] = kwargs.get("async_req", False)
        kwargs["_return_http_data_only"] = kwargs.get("_return_http_data_only", True)
        kwargs["_preload_content"] = kwargs.get("_preload_content", True)
        kwargs["_request_timeout"] = kwargs.get("_request_timeout", None)
        kwargs["_check_input_type"] = kwargs.get("_check_input_type", True)
        kwargs["_check_return_type"] = kwargs.get("_check_return_type", True)
        kwargs["_spec_property_naming"] = kwargs.get("_spec_property_naming", False)
        kwargs["_content_type"] = kwargs.get("_content_type")
        kwargs["_host_index"] = kwargs.get("_host_index")
        kwargs["detector_id"] = detector_id
        return self.create_note_endpoint.call_with_http_info(**kwargs)

    def get_notes(self, detector_id, **kwargs):
        """get_notes  # noqa: E501

        Retrieves all notes from a given detector and returns them in lists, one for each note_category.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.get_notes(detector_id, async_req=True)
        >>> result = thread.get()

        Args:
            detector_id (str): the detector whose notes to retrieve

        Keyword Args:
            _return_http_data_only (bool): response data without head status
                code and headers. Default is True.
            _preload_content (bool): if False, the urllib3.HTTPResponse object
                will be returned without reading/decoding response data.
                Default is True.
            _request_timeout (int/float/tuple): timeout setting for this request. If
                one number provided, it will be total request timeout. It can also
                be a pair (tuple) of (connection, read) timeouts.
                Default is None.
            _check_input_type (bool): specifies if type checking
                should be done one the data sent to the server.
                Default is True.
            _check_return_type (bool): specifies if type checking
                should be done one the data received from the server.
                Default is True.
            _spec_property_naming (bool): True if the variable names in the input data
                are serialized names, as specified in the OpenAPI document.
                False if the variable names in the input data
                are pythonic names, e.g. snake case (default)
            _content_type (str/None): force body content-type.
                Default is None and content-type will be predicted by allowed
                content-types and body.
            _host_index (int/None): specifies the index of the server
                that we want to use.
                Default is read from the configuration.
            async_req (bool): execute request asynchronously

        Returns:
            AllNotes
                If the method is called asynchronously, returns the request
                thread.
        """
        kwargs["async_req"] = kwargs.get("async_req", False)
        kwargs["_return_http_data_only"] = kwargs.get("_return_http_data_only", True)
        kwargs["_preload_content"] = kwargs.get("_preload_content", True)
        kwargs["_request_timeout"] = kwargs.get("_request_timeout", None)
        kwargs["_check_input_type"] = kwargs.get("_check_input_type", True)
        kwargs["_check_return_type"] = kwargs.get("_check_return_type", True)
        kwargs["_spec_property_naming"] = kwargs.get("_spec_property_naming", False)
        kwargs["_content_type"] = kwargs.get("_content_type")
        kwargs["_host_index"] = kwargs.get("_host_index")
        kwargs["detector_id"] = detector_id
        return self.get_notes_endpoint.call_with_http_info(**kwargs)
