import typer
from typing import Union, get_origin
import inspect
from functools import wraps, partial
from groundlight import Groundlight
from typing import Optional

cli_app = typer.Typer()


def remove_self_from_signature(sig):
    params = list(sig.parameters.values())
    params = params[1:]  # Remove the self parameter
    new_sig = sig.replace(parameters=params)
    return new_sig


def class_func_to_cli(method):
    """
    Given the class method, instantiate a Groundlight object that contains the endpoint and api_token and return a function
    that behaves as if the method was called on the Groundlight object
    """

    @wraps(method)
    def wrapper(*args, **kwargs):
        endpoint = kwargs.get("endpoint")
        api_token = kwargs.get("api_token")
        gl = Groundlight(endpoint=endpoint, api_token=api_token)
        # new_method = partial(method, self=gl)
        bound_method = method.__get__(gl)
        print(bound_method(*args, **kwargs))  # this is where we output to the console

    # not recommended practice to directly change annotations, but gets around Typer not supporting Union types
    for name, annotation in method.__annotations__.items():
        if get_origin(annotation) is Union:
            if str in annotation.__args__:
                annotation = str
        wrapper.__annotations__[name] = annotation

    # definitely not standard practice to change the function signature, but this allows us to define functions free from the Groundlight object
    wrapper.__signature__ = remove_self_from_signature(inspect.signature(wrapper))

    return wrapper


def groundlight():
    for name, method in vars(Groundlight).items():
        if callable(method) and not name.startswith("_"):
            cli_func = class_func_to_cli(method)
            cli_app.command()(cli_func)
            print(cli_func.__annotations__)
    cli_app()


if __name__ == "__main__":
    groundlight()
