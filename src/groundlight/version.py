def get_version() -> str:
    try:
        import importlib.metadata  # pylint: disable=import-outside-toplevel

        # Copy the version number from where it's set in pyproject.toml
        return importlib.metadata.version("groundlight")
    except ModuleNotFoundError:
        # importlib.metadata was only added in py3.8
        # We're still supporting py3.7
        return "(version number available in python 3.8+)"
