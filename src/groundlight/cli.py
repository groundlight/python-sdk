import json
import logging
import sys
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from functools import wraps
from importlib.metadata import version as importlib_version
from typing import Any, Optional, Union
from uuid import UUID

import typer
from groundlight_openapi_client.model_utils import OpenApiModel
from pydantic import BaseModel
from typing_extensions import get_origin

from groundlight import ExperimentalApi, Groundlight
from groundlight.client import ApiTokenError

logger = logging.getLogger(__name__)

_TYPER_CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"], "max_content_width": 800}

cli_app = typer.Typer(context_settings=_TYPER_CONTEXT_SETTINGS)


@cli_app.callback(invoke_without_command=True)
def _main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", is_eager=True, help="Show the SDK version and exit."),
):
    if version:
        print(importlib_version("groundlight"))
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


experimental_app = typer.Typer(
    no_args_is_help=True,
    help="Experimental commands — may change or be removed without notice.",
    context_settings=_TYPER_CONTEXT_SETTINGS,
)
cli_app.add_typer(experimental_app, name="exp", rich_help_panel="Subcommands")


def is_cli_representable(annotation) -> bool:
    """Returns True if the annotation is a type Typer can natively represent as a CLI argument.

    Primitive scalar types, Enum subclasses, and Union types (handled separately) are considered
    representable. Complex types like dict, list, bytes, and custom model classes are not.
    """
    if annotation in (str, int, float, bool):
        return True
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return True
    if get_origin(annotation) is Union:
        return True
    return False


def _json_default(obj: Any) -> Any:
    """Fallback serializer for json.dumps for types the stdlib encoder doesn't handle.

    Covers common types that appear in OpenAPI client to_dict() output. Unknown types
    fall back to str() rather than raising, so CLI output is always usable.
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, Enum):
        return obj.value
    return str(obj)


def _format_result(result: Any) -> str:
    """Format a CLI result value as a human-readable string.

    Pydantic models and OpenAPI client objects are serialized to indented JSON.
    Plain dicts and lists are also JSON. Everything else falls back to str().
    """
    if isinstance(result, BaseModel):
        return result.model_dump_json(indent=2)
    if isinstance(result, OpenApiModel):
        return json.dumps(result.to_dict(), indent=2, default=_json_default)
    if isinstance(result, (dict, list)):
        return json.dumps(result, indent=2, default=_json_default)
    return str(result)


def class_func_to_cli(method, is_experimental: bool = False):
    """
    Given a class method, return a wrapper function with the same signature that Typer can
    register as a CLI command. The wrapper instantiates ExperimentalApi at call time (which
    also provides all stable Groundlight methods via inheritance), so a single instantiation
    path serves both stable and experimental commands.

    If is_experimental is True, a warning is printed to stderr before the method runs.
    """

    # We create a fake class and fake method so we have the correct annotations for typer to use.
    # When we wrap the fake method, we only use the fake method's name to look up and call the
    # real method on an ExperimentalApi instance created at call time.
    class FakeClass:
        pass

    fake_instance = FakeClass()
    fake_method = method.__get__(fake_instance, FakeClass)  # pylint: disable=all

    @wraps(fake_method)
    def wrapper(*args, **kwargs):
        if is_experimental:
            print(
                f"Warning: '{fake_method.__name__}' is an experimental command and may change without notice.",
                file=sys.stderr,
            )
        gl = ExperimentalApi()
        # Typer sees the fake method's annotations (for correct CLI argument types), but the
        # actual call goes to the real method on a live ExperimentalApi instance. The fake
        # method's name is identical to the real one, so getattr resolves to the correct
        # implementation, including inherited Groundlight methods.
        bound_method = getattr(gl, fake_method.__name__)
        result = bound_method(*args, **kwargs)
        if result is not None:
            print(_format_result(result))

    # not recommended practice to directly change annotations, but gets around Typer not supporting Union types
    cli_unsupported_params = []
    for name, annotation in method.__annotations__.items():
        if name == "return":
            continue
        if get_origin(annotation) is Union:
            # If we can submit a string, we take the string from the cli
            if str in annotation.__args__:
                wrapper.__annotations__[name] = str
            # Otherwise, we grab the first type that is supported by the CLI
            else:
                found_supported_type = False
                for arg in annotation.__args__:
                    if is_cli_representable(arg):
                        found_supported_type = True
                        wrapper.__annotations__[name] = arg
                        break
                if not found_supported_type:
                    cli_unsupported_params.append(name)
        elif not is_cli_representable(annotation):
            # Proactively flag non-Union types that Typer cannot represent (e.g. dict, list,
            # custom models) before Typer raises a deferred RuntimeError at invocation time.
            cli_unsupported_params.append(name)
    # Ideally we could just not list the unsupported params, but it doesn't seem natively supported by Typer
    # and requires more metaprogramming than makes sense at the moment. For now, we require methods to support str.
    if cli_unsupported_params:
        raise Exception(
            f"Parameter(s) {cli_unsupported_params} on method {method.__name__} have an unsupported type for the CLI."
            " Consider allowing a string representation or adding the method to _CLI_EXCLUDED_METHODS."
        )

    return wrapper


# Methods that should not be exposed as CLI commands. Add a method here if its signature
# cannot be cleanly represented as CLI arguments or if it is not useful as a shell command.
_CLI_EXCLUDED_METHODS = {
    "get_raw_headers",  # returns the API token in plaintext
    "make_generic_api_request",
}

# Desired display order of command groups in the CLI help output.
_GROUP_ORDER = [
    "Account",
    "Detectors",
    "Image Queries",
    "ML Pipelines & Priming",
    "Notes",
    "Utilities",
]

# Maps method names to their rich_help_panel group label for the CLI help output.
# Applies to both stable and experimental commands.
_COMMAND_GROUPS: dict[str, str] = {
    # Account
    "whoami": "Account",
    "get_month_to_date_usage": "Account",
    # Detectors
    "get_detector": "Detectors",
    "get_detector_by_name": "Detectors",
    "list_detectors": "Detectors",
    "create_detector": "Detectors",
    "get_or_create_detector": "Detectors",
    "delete_detector": "Detectors",
    "create_binary_detector": "Detectors",
    "create_counting_detector": "Detectors",
    "create_multiclass_detector": "Detectors",
    "create_bounding_box_detector": "Detectors",
    "create_detector_group": "Detectors",
    "list_detector_groups": "Detectors",
    "create_roi": "Detectors",
    "update_detector_confidence_threshold": "Detectors",
    "update_detector_status": "Detectors",
    "update_detector_escalation_type": "Detectors",
    "reset_detector": "Detectors",
    "update_detector_name": "Detectors",
    "create_text_recognition_detector": "Detectors",
    "get_detector_evaluation": "Detectors",
    "get_detector_metrics": "Detectors",
    "download_mlbinary": "Detectors",
    # Image Queries
    "get_image_query": "Image Queries",
    "list_image_queries": "Image Queries",
    "submit_image_query": "Image Queries",
    "ask_confident": "Image Queries",
    "ask_ml": "Image Queries",
    "ask_async": "Image Queries",
    "wait_for_confident_result": "Image Queries",
    "wait_for_ml_result": "Image Queries",
    "get_image": "Image Queries",
    "add_label": "Image Queries",
    # Notes
    "get_notes": "Notes",
    "create_note": "Notes",
    # ML Pipelines & Priming
    "list_detector_pipelines": "ML Pipelines & Priming",
    "list_priming_groups": "ML Pipelines & Priming",
    "create_priming_group": "ML Pipelines & Priming",
    "get_priming_group": "ML Pipelines & Priming",
    "delete_priming_group": "ML Pipelines & Priming",
    # Utilities
    "edge_base_url": "Utilities",
    "get_raw_headers": "Utilities",
}


def _cli_sort_key(item: tuple) -> tuple:
    """Sort key for CLI command registration that controls group and within-group ordering.

    Commands are ordered first by their group's position in _GROUP_ORDER, then alphabetically
    by method name within each group.
    """
    name, _ = item
    group = _COMMAND_GROUPS.get(name)
    order = _GROUP_ORDER.index(group) if group in _GROUP_ORDER else len(_GROUP_ORDER)
    return (order, name)


def _is_cli_eligible(name: str, method, skip: set) -> bool:
    """Returns True if a class method should be registered as a CLI command."""
    return callable(method) and not name.startswith("_") and name not in skip and name not in _CLI_EXCLUDED_METHODS


def _register_commands(source_cls: type, app: typer.Typer, *, skip: Optional[set] = None) -> set:
    """Register all eligible public methods from source_cls as commands on the given Typer app.

    Returns the set of registered method names.
    """
    is_experimental = source_cls is ExperimentalApi
    skip = skip or set()
    registered = set()
    for name, method in sorted(vars(source_cls).items(), key=_cli_sort_key):
        if not _is_cli_eligible(name, method, skip):
            continue
        cli_func = class_func_to_cli(method, is_experimental=is_experimental)
        app.command(rich_help_panel=_COMMAND_GROUPS[name])(cli_func)
        registered.add(name)
    return registered


def groundlight():
    """Entry point for the groundlight CLI."""
    try:
        stable_names = _register_commands(Groundlight, cli_app)
        _register_commands(ExperimentalApi, experimental_app, skip=stable_names)
        cli_app()
    except ApiTokenError as e:
        print(e)


if __name__ == "__main__":
    groundlight()
