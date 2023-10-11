from functools import wraps
from typing import Union

import typer
from typing_extensions import get_origin

from groundlight import Groundlight
from groundlight.client import ApiTokenError
from groundlight.config import API_TOKEN_HELP_MESSAGE

cli_app = typer.Typer(no_args_is_help=True, context_settings={"help_option_names": ["-h", "--help"]})


def class_func_to_cli(method):
    """
    Given the class method, simplify the typing on the inputs so that Typer can accept the method
    """

    # We create a temporary class to bind the method to so we have the correct annotations for typer to use
    # The first thing we'll do when we actually call the method is to bind it to a proper Groundlight instance
    class fake_class:
        pass

    fake_instance = fake_class()
    fake_bound_method = method.__get__(fake_instance, fake_class)

    @wraps(fake_bound_method)
    def wrapper(*args, **kwargs):
        gl = Groundlight()
        gl_bound_method = fake_instance.fake_bound_method.__get__(gl, Groundlight)
        print(gl_bound_method(*args, **kwargs))  # this is where we output to the console

    # not recommended practice to directly change annotations, but gets around Typer not supporting Union types
    for name, annotation in method.__annotations__.items():
        if get_origin(annotation) is Union:
            if str in annotation.__args__:
                wrapper.__annotations__[name] = str
            else:
                wrapper.__annotations__[name] = annotation

    return wrapper


def groundlight():
    try:
        # For each method in the Groundlight class, create a function that can be called from the command line
        for name, method in vars(Groundlight).items():
            if callable(method) and not name.startswith("_"):
                cli_func = class_func_to_cli(method)
                cli_app.command()(cli_func)
        cli_app()
    except ApiTokenError:
        print(API_TOKEN_HELP_MESSAGE)


if __name__ == "__main__":
    groundlight()
