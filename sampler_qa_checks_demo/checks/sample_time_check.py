from typing import List
from datetime import datetime, timedelta
import HilltopHost
from .i_check import ICheck
from HilltopHost.Sampler import QACheck, QACheckSeverity
from .. import utils

class SampleTimeCheck(ICheck):
    """
    An implementation of the ICheck interface that checks a sample.
    """
    
    def __init__(self, config, connection):
        super().__init__(config, connection)
        self.age_limit = self.config.get("age_limit", 3) # default to 3 days ago
        HilltopHost.LogInfo(f"sampler_qa_checks_demo - SampleCheckTime is using an age limit of {self.age_limit} days")        
    
    def perform_checks(self, context) -> List[QACheck]:
        # HilltopHost.LogInfo(f"sampler_qa_checks_demo - SampleCheckTime checking sample {context.SampleID}")
        # HilltopHost.LogInfo(f"sampler_qa_checks_demo - SampleCheckTime sample {str(utils.dump_object(context))}")
        if context.StatusID != HilltopHost.RunStatus.SOME_RESULTS_BACK:
            return []
        
        if not context.SampleTime:
            return []
        
        today = datetime.now()
        n_days_ago = today - timedelta(days=self.age_limit)
        status = context.StatusID
        sample_time = datetime.fromisoformat(context.SampleTime)
        # HilltopHost.LogInfo(f"sampler_qa_checks_demo - SampleCheckTime sample time is {sample_time}")        
        if sample_time < n_days_ago:
            details = f"Sample ID {context.SampleID} has only some results back, but sample time is {sample_time} and older than {self.age_limit} days"
            HilltopHost.LogWarning(f"sampler_qa_checks_demo - SampleCheckTime found {details}")
            qa_check = QACheck()
            qa_check.Title = "Sample is missing results"
            qa_check.RunID = context.RunID
            qa_check.SampleID = context.SampleID
            qa_check.Severity = QACheckSeverity.Warning
            qa_check.Details = details
            qa_check.Label = "sample_check_time"
            return [qa_check]
        # qa_check = QACheck()
        # qa_check.Title = "Sample Check"
        # qa_check.RunID = context.RunID
        # qa_check.SampleID = context.SampleID
        # qa_check.Severity = QACheckSeverity.OK
        # qa_check.Label = "sample_check"
        return []
