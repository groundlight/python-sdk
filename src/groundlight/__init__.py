# flake8: noqa
# Add useful imports from the generated code here at the top level, as a convenience.
from openapi_client import ApiException

# Imports from our code
from .client import Groundlight

try:
    import importlib.metadata

    # Copy the version number from where it's set in pyproject.toml
    __version__ = importlib.metadata.version("groundlight")
except ModuleNotFoundError:
    # importlib.metadata was only added in py3.8
    # We're still supporting py3.7
    __version__ = "(version number available in python 3.8+)"
