from typing import List
from datetime import datetime, timedelta
import HilltopHost
from .i_check import ICheck
from HilltopHost.Sampler import QACheck, QACheckSeverity

class SampleTimeCheck(ICheck):
    """
    An implementation of the ICheck interface that checks a sample.
    """
    
    def __init__(self, config, connection):
        super().__init__(config, connection)
        self.age_limit = self.config.get("age_limit", 3) # default to 3 days ago
        HilltopHost.LogInfo(f"sampler_qa_checks_demo - SampleTimeCheck is using an age limit of {self.age_limit} days")        
    
    def perform_checks(self, run_id, context) -> List[QACheck]:
        # we're only checking samples that are old, yet still not complete
        if context.StatusID != HilltopHost.RunStatus.SOME_RESULTS_BACK:
            return []
        
        if not context.SampleTime:
            return []
        
        today = datetime.now()
        n_days_ago = today - timedelta(days=self.age_limit)
        sample_time = datetime.fromisoformat(context.SampleTime)
        if sample_time < n_days_ago:
            details = f"Sample ID {context.SampleID} has only some results back, but sample time is {sample_time} and older than {self.age_limit} days"
            qa_check = QACheck()
            qa_check.Title = "Sample is missing results"
            qa_check.RunID = run_id
            qa_check.SampleID = context.SampleID
            qa_check.Severity = QACheckSeverity.Warning
            qa_check.Details = details
            qa_check.Label = "sample_check_time"
            return [qa_check]
        return []
