from datetime import datetime

from groundlight import ExperimentalApi


def test_metrics_and_evaluation(gl_experimental: ExperimentalApi):
    name = f"Test metrics and evaluation {datetime.utcnow()}"
    det = gl_experimental.create_detector(name, "test_query")
    for i in range(6):
        iq = gl_experimental.submit_image_query(
            det, "test/assets/cat.jpeg", wait=0, patience_time=10, human_review="NEVER"
        )
        gl_experimental.add_label(iq, "YES")
        iq = gl_experimental.submit_image_query(
            det, "test/assets/cat.jpeg", wait=0, patience_time=10, human_review="NEVER"
        )
        gl_experimental.add_label(iq, "NO")
    metrics = gl_experimental.get_detector_metrics(det.id)
    assert metrics["summary"] is not None
    assert metrics["summary"]["num_ground_truth"] is not None
    assert metrics["summary"]["num_current_source_human"] is not None
    assert metrics["summary"]["class_counts"] is not None
    assert metrics["summary"]["unconfident_counts"] is not None
    assert metrics["summary"]["total_iqs"] is not None

    # NOTE: this implicitly tests how quickly the evaluation is made available
    evaluation = gl_experimental.get_detector_evaluation(det.id)
    assert evaluation["evaluation_results"]["kfold_pooled__balanced_accuracy"] is not None
    assert evaluation["evaluation_results"]["kfold_pooled__positive_accuracy"] is not None
    assert evaluation["evaluation_results"]["kfold_pooled__negative_accuracy"] is not None
    assert evaluation["evaluation_results"]["balanced_system_accuracies"] is not None
    assert evaluation["evaluation_results"]["positive_system_accuracies"] is not None
    assert evaluation["evaluation_results"]["negative_system_accuracies"] is not None
