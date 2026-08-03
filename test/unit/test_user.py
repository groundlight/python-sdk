from groundlight import Groundlight
from model import Group, Me


def test_whoami(gl: Groundlight):
    user = gl.whoami()
    assert user is not None
    assert isinstance(user, str)


def test_me(gl: Groundlight):
    """me() returns structured identity including group from /v1/me."""
    me = gl.me()
    assert isinstance(me, Me)
    assert me.email
    assert me.username
    assert isinstance(me.group, Group)
    assert me.group.id
    assert me.group.name
    assert gl.whoami() == me.email
