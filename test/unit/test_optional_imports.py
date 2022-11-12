from typing import Union

from groundlight.optional_imports import UnavailableModule


def test_type_hints():
    e = ModuleNotFoundError("perfect_perception module does not exist")
    failed_import = UnavailableModule(e)
    # Check that the UnavailableModule class can be used in type hints.
    def typed_method(foo: Union[failed_import, str]):
        print(foo)

