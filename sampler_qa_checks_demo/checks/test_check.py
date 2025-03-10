import HilltopHost
from typing import List
from .i_check import ICheck
from HilltopHost.Sampler import QACheck, QACheckSeverity


class TestCheck(ICheck):
    """
    A simple implementation of the ICheck interface that logs a message.
    """
    def perform_checks(self, run_id, context) -> List[QACheck]:

        if self.has_check_result(context, "test_check"):
            return

        HilltopHost.LogInfo("sampler_qa_checks_demo - TestCheck called")
        qa_check = QACheck()
        qa_check.Title = "Test Check"
        qa_check.RunID = run_id
        qa_check.Severity = QACheckSeverity.OK
        qa_check.Label = "test_check"
        return [qa_check]
