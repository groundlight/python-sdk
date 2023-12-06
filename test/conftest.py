import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--edge-endpoint",
        action="store_true",
        default=False,
        help=(
            "skip tests for features that are unsupported on the edge-endpoint. Additonally, run other tests that"
            " ensure that good errors are returned from the edge-endpoint."
        ),
    )
