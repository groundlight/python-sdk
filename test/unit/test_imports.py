# pylint: disable=unused-import, import-outside-toplevel
# flake8: noqa: F401


def test_imports():
    """Test that all modules can be imported."""
    import groundlight
    from groundlight import ApiException, Groundlight, binary_labels, client, config, images, internalapi
