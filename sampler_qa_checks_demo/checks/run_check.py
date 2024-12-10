import HilltopHost
from typing import List
from .i_check import ICheck
from HilltopHost.Sampler import QACheck, QACheckSeverity

class RunCheck(ICheck):
    """
    A run-level implementation of the ICheck interface that checks the run name length.
    """
    def perform_checks(self, context) -> List[QACheck]:
        name_max_length = self.config.get('name_max_length')
        if name_max_length and len(context.RunName) > name_max_length:
            qa_check = QACheck()
            qa_check.Title = "Run name is too long"
            qa_check.RunID = context.RunID
            qa_check.Severity = QACheckSeverity.Information
            qa_check.Details = f"Run name '{context.RunName}' is {len(context.RunName)} characters long, which exceeds the maximum of {name_max_length}."
            qa_check.Label = "run_check_name_max_length"
            return [qa_check]
