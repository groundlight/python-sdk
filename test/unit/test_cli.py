import os
import re
import subprocess
from datetime import datetime
from unittest.mock import patch


def test_list_detector():
    completed_process = subprocess.run(
        ["groundlight", "list-detectors"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert completed_process.returncode == 0


def test_detector_and_image_queries():
    # test creating a detector
    test_detector_name = f"testdetector {datetime.utcnow()}"
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
    )
    assert completed_process.returncode == 0
    det_id_on_create = re.search("id='([^']+)'", completed_process.stdout).group(1)
    # The output of the create-detector command looks something like:
    # id='det_abc123'
    # type=<DetectorTypeEnum.detector: 'detector'>
    # created_at=datetime.datetime(2023, 8, 30, 18, 3, 9, 489794,
    # tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=61200)))
    # name='testdetector 2023-08-31 01:03:09.039448' query='testdetector'
    # group_name='__DEFAULT' confidence_threshold=0.9

    # test getting detectors
    completed_process = subprocess.run(
        ["groundlight", "get-detector-by-name", test_detector_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert completed_process.returncode == 0
    det_id_on_get = re.search("id='([^']+)'", completed_process.stdout).group(1)
    assert det_id_on_create == det_id_on_get
    completed_process = subprocess.run(
        ["groundlight", "get-detector", det_id_on_create],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
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
    )
    assert completed_process.returncode == 0


@patch.dict(os.environ, {"GROUNDLIGHT_API_TOKEN": None})
def test_help():
    completed_process = subprocess.run(["groundlight"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert completed_process.returncode == 0
    completed_process = subprocess.run(["groundlight", "-h"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert completed_process.returncode == 0
    completed_process = subprocess.run(
        ["groundlight", "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    assert completed_process.returncode == 0
    completed_process = subprocess.run(
        ["groundlight", "get-detector", "-h"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    assert completed_process.returncode == 0


def test_bad_commands():
    completed_process = subprocess.run(
        ["groundlight", "wat"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    assert completed_process.returncode != 0
    # commands use dashes, not underscores
    completed_process = subprocess.run(
        ["groundlight", "list_detectors"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    assert completed_process.returncode != 0
