from datetime import datetime

import pytest
from groundlight import ExperimentalApi


def test_metrics_and_evaluation(gl_experimental: ExperimentalApi):
    name = f"Test metrics and evaluation {datetime.utcnow()}"
    det = gl_experimental.create_detector(name, "test_query")
    iq1 = gl_experimental.submit_image_query(det, "test/assets/cat.jpeg")
    for i in range(10):
        gl_experimental.add_label(iq1, "YES")
        gl_experimental.add_label(iq1, "NO")
    metrics = gl_experimental.get_detector_metrics(det.id)

    evaluation = gl_experimental.evaluate_detector(det.id)
