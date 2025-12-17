import HilltopHost
from typing import List
from .i_check import ICheck
from HilltopHost.Sampler import QACheck, QACheckSeverity


class DemoCheck(ICheck):
    """
    A simple implementation of the ICheck interface that logs a message.
    """
    def perform_checks(self, run_id, context) -> List[QACheck]:

        if self.has_check_result(context, "demo_check"):
            return

        HilltopHost.LogInfo("sampler_qa_checks_demo - DemoCheck called")
        qa_check = QACheck()
        qa_check.Title = "Demo Check"
        qa_check.RunID = run_id
        qa_check.Severity = QACheckSeverity.OK
        qa_check.Label = "demo_check"
        return [qa_check]
