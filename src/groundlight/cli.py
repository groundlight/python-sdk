from functools import wraps
from typing import Union

import typer
from typing_extensions import get_origin

from groundlight import Groundlight
from groundlight.client import ApiTokenError

cli_app = typer.Typer(
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"], "max_content_width": 800},
)


def is_cli_supported_type(annotation):
    """
    Check if the annotation is a type that can be supported by the CLI
    str is a supported type, but is given precedence over other types
    """
    return annotation in (int, float, bool)


def class_func_to_cli(method):
    """
    Given the class method, create a method with the identical signature to provide the help documentation and
    but only instantiates the class when the method is actually called.
    """

    # We create a fake class and fake method so we have the correct annotations for typer to use
    # When we wrap the fake method, we only use the fake method's name to access the real method
    # and attach it to a Groundlight instance that we create at function call time
    class FakeClass:
        pass

    fake_instance = FakeClass()
    fake_method = method.__get__(fake_instance, FakeClass)  # pylint: disable=all

    @wraps(fake_method)
    def wrapper(*args, **kwargs):
        gl = Groundlight()
        gl_method = vars(Groundlight)[fake_method.__name__]
        gl_bound_method = gl_method.__get__(gl, Groundlight)  # pylint: disable=all
        print(gl_bound_method(*args, **kwargs))  # this is where we output to the console

    # not recommended practice to directly change annotations, but gets around Typer not supporting Union types
    cli_unsupported_params = []
    for name, annotation in method.__annotations__.items():
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
    # Ideally we could just not list the unsupported params, but it doesn't seem natively supported by Typer
    # and requires more metaprogamming than makes sense at the moment. For now, we require methods to support str
    for param in cli_unsupported_params:
        raise Exception(
            f"Parameter {param} on method {method.__name__} has an unsupported type for the CLI. Consider allowing a"
            " string representation or writing a custom exception inside the method"
        )

    return wrapper


def groundlight():
    try:
        # For each method in the Groundlight class, create a function that can be called from the command line
        for name, method in vars(Groundlight).items():
            if callable(method) and not name.startswith("_"):
                cli_func = class_func_to_cli(method)
                cli_app.command()(cli_func)
        cli_app()
    except ApiTokenError as e:
        print(e)


if __name__ == "__main__":
    groundlight()
