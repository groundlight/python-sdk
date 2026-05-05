import os
import re
import subprocess
from typing import Callable
from unittest.mock import patch

from groundlight import ExperimentalApi, Groundlight
from groundlight.cli import _CLI_EXCLUDED_METHODS, _COMMAND_GROUPS, _is_cli_eligible


def test_whoami():
    completed_process = subprocess.run(
        ["groundlight", "whoami"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
    )
    assert completed_process.returncode == 0


def test_list_detector():
    completed_process = subprocess.run(
        ["groundlight", "list-detectors"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    assert completed_process.returncode == 0


def test_detector_and_image_queries(detector_name: Callable):
    # test creating a detector
    test_detector_name = detector_name("testdetector")
    completed_process = subprocess.run(
        [
            "groundlight",
            "create-detector",
            test_detector_name,
            "testdetector",
            "--confidence-threshold",
            "0.9",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    assert completed_process.returncode == 0
    match = re.search(r'"id":\s*"([^"]+)"', completed_process.stdout)
    assert match is not None
    det_id_on_create = match.group(1)

    # test getting detectors
    completed_process = subprocess.run(
        ["groundlight", "get-detector-by-name", test_detector_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    assert completed_process.returncode == 0
    match = re.search(r'"id":\s*"([^"]+)"', completed_process.stdout)
    assert match is not None
    det_id_on_get = match.group(1)
    assert det_id_on_create == det_id_on_get
    completed_process = subprocess.run(
        ["groundlight", "get-detector", det_id_on_create],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    assert completed_process.returncode == 0

    # test submitting an image
    completed_process = subprocess.run(
        [
            "groundlight",
            "submit-image-query",
            det_id_on_create,
            "test/assets/cat.jpeg",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    assert completed_process.returncode == 0


@patch.dict(os.environ, {})
def test_help():
    completed_process = subprocess.run(
        ["groundlight"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
    )
    assert completed_process.returncode == 0
    completed_process = subprocess.run(
        ["groundlight", "-h"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
    )
    assert completed_process.returncode == 0
    completed_process = subprocess.run(
        ["groundlight", "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
    )
    assert completed_process.returncode == 0
    completed_process = subprocess.run(
        ["groundlight", "get-detector", "-h"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
    )
    assert completed_process.returncode == 0


def test_version():
    for flag in ("--version", "-v"):
        completed_process = subprocess.run(
            ["groundlight", flag],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        assert completed_process.returncode == 0
        assert re.match(r"\d+\.\d+\.\d+", completed_process.stdout.strip())


def test_experimental_subcommand():
    completed_process = subprocess.run(
        ["groundlight", "exp", "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    assert completed_process.returncode == 0
    assert "list-priming-groups" in completed_process.stdout


def test_bad_commands():
    completed_process = subprocess.run(
        ["groundlight", "wat"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
    )
    assert completed_process.returncode != 0
    # commands use dashes, not underscores
    completed_process = subprocess.run(
        ["groundlight", "list_detectors"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
    )
    assert completed_process.returncode != 0


def test_all_cli_commands_have_group():
    """Enforce that every method registered in the CLI has an entry in _COMMAND_GROUPS.

    All stable methods and all experimental methods not in _CLI_EXCLUDED_METHODS must have
    a group. If a new method is added to Groundlight or ExperimentalApi without a group
    assignment, this test fails with a clear message listing what's missing.
    """
    stable_names = {n for n, m in vars(Groundlight).items() if _is_cli_eligible(n, m, skip=set())}

    missing = []

    for name in stable_names:
        if name not in _COMMAND_GROUPS:
            missing.append(f"stable: {name}")

    for name, method in vars(ExperimentalApi).items():
        if not _is_cli_eligible(name, method, skip=stable_names):
            continue
        if name not in _COMMAND_GROUPS:
            missing.append(f"experimental: {name}")

    assert not missing, "Methods registered in CLI but missing from _COMMAND_GROUPS:\n" + "\n".join(
        f"  {m}" for m in sorted(missing)
    )
