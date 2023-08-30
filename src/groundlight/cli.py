import typer
from typing import Union, get_origin
import inspect
from groundlight import Groundlight
from typing import Optional

cli_app = typer.Typer()


def method_signature_to_function_signature(sig):
    """
    Takes a method signature and converts it to the appropriate signature for the cli
    Takes signatures that potentially has Union types and converts them to strings to gets around Typer not supporting Union types in the signature
    removes the self parameter as we translate from methods to stand alone functions
    """
    params = list(sig.parameters.values())
    for i, param in enumerate(sig.parameters.values()):
        if get_origin(param.annotation) is Union:
            params[i] = param.replace(annotation=str)
    params = params[1:]  # Remove the self parameter
    new_sig = sig.replace(parameters=params)
    return new_sig


def class_func_to_cli(method):
    def cli_func(*args, endpoint: Optional[str] = None, api_token: Optional[str] = None, **kwargs):
        gl = Groundlight(endpoint=endpoint, api_token=api_token)
        bound_method = method.__get__(gl)
        print(bound_method(*args, **kwargs))

    print(method.__name__)
    print(method.__annotations__)
    cli_func.__name__ = method.__name__  # Preserve the function name in the cli version
    cli_func.__doc__ = method.__doc__  # Preserve docstring in the cli version
    cli_func.__signature__ = method_signature_to_function_signature(
        inspect.signature(method)
    )  # Preserve signature in the cli version
    print(cli_func.__signature__)
    print(cli_func.__annotations__)
    print("\n" * 2)
    return cli_func


def groundlight():
    for name, method in vars(Groundlight).items():
        if callable(method) and not name.startswith("_"):
            cli_func = class_func_to_cli(method)
            cli_app.command()(cli_func)
    cli_app()


if __name__ == "__main__":
    groundlight()
