from groundlight import ExperimentalApi
from unittest.mock import patch
from model import ImageQuery, Source, BinaryClassificationResult, Label


def test_wait_for_confident_result_returns_immediately_when_no_better_result_expected(
    gl_experimental: ExperimentalApi, initial_iq: ImageQuery
):
    with patch.object(gl_experimental, "_wait_for_result") as mock_wait_for_result:
        # Should not wait if the image query is done processing
        initial_iq.done_processing = True
        gl_experimental.wait_for_confident_result(initial_iq)
        mock_wait_for_result.assert_not_called()

        # Should not wait if the result is from the edge
        initial_iq.done_processing = False
        initial_iq.result = BinaryClassificationResult(source=Source.EDGE, label=Label.YES)
        gl_experimental.wait_for_confident_result(initial_iq)
        mock_wait_for_result.assert_not_called()
