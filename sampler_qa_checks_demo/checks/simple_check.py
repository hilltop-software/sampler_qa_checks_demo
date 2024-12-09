import HilltopHost
from typing import List
from .i_check import ICheck
from HilltopHost.Sampler import QACheck, QACheckSeverity

class SimpleCheck(ICheck):
    """
    A simple implementation of the ICheck interface that logs a message.
    """
    def perform_checks(self, context) -> List[QACheck]:
        HilltopHost.LogInfo("sampler_qa_checks_demo - SimpleCheck called")
        qa_check = QACheck()
        qa_check.Title = "Simple Check"
        qa_check.RunID = context.RunID
        qa_check.Severity = QACheckSeverity.OK
        qa_check.Label = "simple_check"
        return [qa_check]
