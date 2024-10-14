from datetime import datetime

import pytest
from groundlight import Groundlight

def test_whoami(gl: Groundlight):
    user = gl.whoami()
    assert user is not None
    assert isinstance(user, str)