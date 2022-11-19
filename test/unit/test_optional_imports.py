from typing import Union

import pytest

from groundlight.optional_imports import UnavailableModule


@pytest.fixture
def failed_import() -> type:
    e = ModuleNotFoundError("perfect_perception module does not exist")
    return UnavailableModule(e)


def test_type_hints(failed_import):
    # Check that the UnavailableModule class can be used in type hints.
    def typed_method(foo: Union[failed_import, str]):
        print(foo)

    assert True, "Yay UnavailableModule can be used in a type hint"


@pytest.mark.skip("Would be nice if this works, but it doesn't")
def test_raises_exception(failed_import):
    # We'd like the UnavailableModule object to raise an exception
    # anytime you access it, where the exception is a RuntimeError
    # but builds on the original ImportError so you can see what went wrong.
    # The old version had this, but didn't work with modern type-hinting.
    with pytest.raises(RuntimeError):
        failed_import.foo
