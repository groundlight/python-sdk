import json
import logging
import sys
from datetime import datetime
from enum import Enum
from functools import wraps
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

experimental_app = typer.Typer(
    no_args_is_help=True,
    help="Experimental commands — may change or be removed without notice.",
    context_settings={"help_option_names": ["-h", "--help"], "max_content_width": 800},
)
cli_app.add_typer(experimental_app, name="experimental")
cli_app.add_typer(experimental_app, name="exp")


_CLI_PRIMITIVE_TYPES = (str, int, float, bool)


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
    if annotation in _CLI_PRIMITIVE_TYPES:
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


def groundlight():
    """Entry point for the groundlight CLI."""
    try:
        stable_names = {n for n, m in vars(Groundlight).items() if callable(m) and not n.startswith("_")}

        for name, method in vars(Groundlight).items():
            if callable(method) and not name.startswith("_"):
                cli_func = class_func_to_cli(method)
                cli_app.command()(cli_func)

        for name, method in vars(ExperimentalApi).items():
            if not callable(method) or name.startswith("_") or name in stable_names:
                continue
            try:
                cli_func = class_func_to_cli(method, is_experimental=True)
                experimental_app.command()(cli_func)
            except Exception as e:  # pylint: disable=broad-except
                logger.debug("Skipping experimental CLI command '%s': %s", name, e)

        cli_app()
    except ApiTokenError as e:
        print(e)


if __name__ == "__main__":
    groundlight()
