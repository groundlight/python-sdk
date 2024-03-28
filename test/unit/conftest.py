import pytest
from groundlight import ExperimentalApi


@pytest.fixture(name="gl")
def _gl() -> ExperimentalApi:
    return ExperimentalApi()
