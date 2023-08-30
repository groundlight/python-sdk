import subprocess


def test_list_detector():
    completed_process = subprocess.run(
        ["groundlight", "list-detectors"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )


def test_create_then_get_detector():
    completed_process = subprocess.run(
        ["groundlight", "create-detector", "testdetector", "testdetector", "--confidence-threshold", "0.9"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    print(completed_process.stdout)
    assert completed_process.returncode == 0
    completed_process.returncode = subprocess.run(
        ["groundlight", "get-detector", "test_detector"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    print(completed_process.stdout)
    assert completed_process.returncode == 0


def test_bad_commands():
    completed_process = subprocess.run(["groundlight"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert completed_process.returncode != 0
    completed_process = subprocess.run(
        ["groundlight", "wat"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    assert completed_process.returncode != 0
    # commands use dashes, not underscores
    completed_process = subprocess.run(
        ["groundlight", "list_detectors"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    assert completed_process.returncode != 0
