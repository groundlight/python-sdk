import json
import logging
import sys
from datetime import datetime
from enum import Enum
from functools import wraps
from importlib.metadata import version as importlib_version
from typing import Any, Union

import typer
from groundlight_openapi_client.model_utils import OpenApiModel
from pydantic import BaseModel
from typing_extensions import get_origin

from groundlight import ExperimentalApi, Groundlight
from groundlight.client import ApiTokenError

logger = logging.getLogger("groundlight.sdk")

cli_app = typer.Typer(
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"], "max_content_width": 800},
)


@cli_app.callback(invoke_without_command=True)
def _main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", is_eager=True, help="Show the SDK version and exit."),
):
    if version:
        print(importlib_version("groundlight"))
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


experimental_app = typer.Typer(
    no_args_is_help=True,
    help="Experimental commands — may change or be removed without notice.",
    context_settings={"help_option_names": ["-h", "--help"], "max_content_width": 800},
)
cli_app.add_typer(experimental_app, name="exp", rich_help_panel="Subcommands")
cli_app.add_typer(experimental_app, name="experimental", hidden=True)


def is_cli_supported_type(annotation):
    """
    Check if the annotation is a type that can be supported by the CLI
    str is a supported type, but is given precedence over other types
    """
    return annotation in (int, float, bool)


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
    """Fallback serializer for json.dumps — handles datetime values."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _format_result(result: Any) -> str:
    """Format a CLI result value as a human-readable, jq-compatible string.

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
                    if is_cli_supported_type(arg):
                        found_supported_type = True
                        wrapper.__annotations__[name] = arg
                        break
                if not found_supported_type:
                    cli_unsupported_params.append(name)
        elif is_experimental and not is_cli_representable(annotation):
            # For experimental methods only: proactively flag non-Union types that Typer cannot
            # represent (e.g. dict, list, custom models) so the caller can skip them gracefully
            # before Typer raises a deferred RuntimeError at cli_app() invocation time.
            cli_unsupported_params.append(name)
    # Ideally we could just not list the unsupported params, but it doesn't seem natively supported by Typer
    # and requires more metaprogamming than makes sense at the moment. For now, we require methods to support str
    for param in cli_unsupported_params:
        raise Exception(
            f"Parameter {param} on method {method.__name__} has an unsupported type for the CLI. Consider allowing a"
            " string representation or writing a custom exception inside the method"
        )

    return wrapper


# Methods to exclude from the CLI entirely. These may be too complex to express
# as CLI commands, deprecated, or otherwise not useful from a shell context.
_CLI_EXCLUDED_METHODS = {
    "make_action",
    "create_rule",
    "get_rule",
    "delete_rule",
    "list_rules",
    "delete_all_rules",
    "start_inspection",
    "update_inspection_metadata",
    "stop_inspection",
}

# Desired display order of command groups in the CLI help output.
# Groups not listed here appear after the listed ones.
_GROUP_ORDER = [
    "Account",
    "Detectors",
    "Image Queries",
    "ML Pipelines & Priming",
    "Notes",
    "Utilities",
]

# Maps method names to their rich_help_panel group label for the CLI help output.
# Applies to both stable and experimental commands. Methods not listed here fall
# into the default "Commands" panel.
_COMMAND_GROUPS: dict = {
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

    Commands are ordered first by their group's position in _GROUP_ORDER (ungrouped last),
    then alphabetically by method name within each group.
    """
    name, _ = item
    group = _COMMAND_GROUPS.get(name)
    group_rank = _GROUP_ORDER.index(group) if group in _GROUP_ORDER else len(_GROUP_ORDER)
    return (group_rank, name)


def groundlight():
    """Entry point for the groundlight CLI."""
    try:
        stable_names = {n for n, m in vars(Groundlight).items() if callable(m) and not n.startswith("_")}

        for name, method in sorted(vars(Groundlight).items(), key=_cli_sort_key):
            if callable(method) and not name.startswith("_") and name not in _CLI_EXCLUDED_METHODS:
                cli_func = class_func_to_cli(method)
                cli_app.command(rich_help_panel=_COMMAND_GROUPS.get(name))(cli_func)

        for name, method in sorted(vars(ExperimentalApi).items(), key=_cli_sort_key):
            if not callable(method) or name.startswith("_") or name in stable_names or name in _CLI_EXCLUDED_METHODS:
                continue
            try:
                cli_func = class_func_to_cli(method, is_experimental=True)
                experimental_app.command(rich_help_panel=_COMMAND_GROUPS.get(name))(cli_func)
            except Exception as e:  # pylint: disable=broad-except
                logger.debug("Skipping experimental CLI command '%s': %s", name, e)

        cli_app()
    except ApiTokenError as e:
        print(e)


if __name__ == "__main__":
    groundlight()
