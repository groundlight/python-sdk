from groundlight import Groundlight
from model import Group, Me


def test_whoami(gl: Groundlight):
    user = gl.whoami()
    assert user is not None
    assert isinstance(user, str)


def test_me(gl: Groundlight):
    """me() returns structured identity including groups from /v1/me."""
    me = gl.me()
    assert isinstance(me, Me)
    assert me.email
    assert me.username
    assert isinstance(me.groups, list)
    assert len(me.groups) >= 1
    assert all(isinstance(group, Group) for group in me.groups)
    assert all(group.id and group.name for group in me.groups)
    assert gl.whoami() == me.email
