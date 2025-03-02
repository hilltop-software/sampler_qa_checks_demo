import HilltopHost
from typing import List
from .i_check import ICheck
from HilltopHost.Sampler import QACheck, QACheckSeverity
from .. import utils

class RunNameCheck(ICheck):
    """
    A run-level implementation of the ICheck interface that checks the run name length.
    """
    
    def __init__(self, config, repository):
        super().__init__(config, repository)
        self.name_max_length = self.config.get("name_max_length", 100) # default to 100 characters
        HilltopHost.LogInfo(f"sampler_qa_checks_demo - RunNameCheck is using a limit of {self.name_max_length} characters")        
    

    def perform_checks(self, run_id, context) -> List[QACheck]:
        if self.disabled:
            return []
        if self.has_check_result(context, "run_name_check"):
            return []
        if len(context.RunName) > self.name_max_length:
            qa_check = QACheck()
            qa_check.Title = "Run name is too long"
            qa_check.RunID = run_id
            qa_check.Severity = QACheckSeverity.Information
            qa_check.Details = f"Run name '{context.RunName}' is {len(context.RunName)} characters long, which exceeds the maximum of {self.name_max_length}."
            qa_check.Label = "run_name_check"
            return [qa_check]
