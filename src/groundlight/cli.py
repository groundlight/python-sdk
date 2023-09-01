import typer
from typing import Union, get_origin
import inspect
from functools import wraps, partial
from groundlight import Groundlight
from typing import Optional

cli_app = typer.Typer()


def class_func_to_cli(method):
    """
    Given the class method, instantiate a Groundlight object that contains the endpoint and api_token and return a function
    that behaves as if the method was called on the Groundlight object
    """

    @wraps(method)
    def wrapper(*args, **kwargs):
        print(method(*args, **kwargs))  # this is where we output to the console

    # not recommended practice to directly change annotations, but gets around Typer not supporting Union types
    for name, annotation in method.__annotations__.items():
        if get_origin(annotation) is Union:
            if str in annotation.__args__:
                annotation = str
        wrapper.__annotations__[name] = annotation

    return wrapper


def groundlight():
    gl = Groundlight()
    for name, method in vars(Groundlight).items():
        if callable(method) and not name.startswith("_"):
            attached_method = method.__get__(gl)
            cli_func = class_func_to_cli(attached_method)
            cli_app.command()(cli_func)
    cli_app()


if __name__ == "__main__":
    groundlight()
