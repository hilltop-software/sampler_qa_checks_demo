from typing import List
from datetime import datetime, timedelta
import HilltopHost
from .i_check import ICheck
from HilltopHost.Sampler import QACheck, QACheckSeverity


class MissingResultsCheck(ICheck):
    """
    An implementation of the ICheck interface that checks a sample.
    """

    def __init__(self, config, repository):
        super().__init__(config, repository)
        if self.disabled:
            return
        self.age_limit = self.config.get("age_limit", 3)  # default to 3 days ago
        HilltopHost.LogInfo(f"sampler_qa_checks_demo - MissingResultsCheck is using an age limit of {self.age_limit} days")

    def perform_checks(self, run_id, context) -> List[QACheck]:
        if self.has_check_result(context, "missing_results_check"):
            return

        # we're only checking samples that are old, yet still not complete
        if context.StatusID != HilltopHost.RunStatus.SOME_RESULTS_BACK:
            return

        if not context.SampleTime:
            return

        today = datetime.now()
        n_days_ago = today - timedelta(days=self.age_limit)
        sample_time = datetime.fromisoformat(context.SampleTime)
        if sample_time < n_days_ago:
            details = f"Sample ID {context.SampleID} has only some results back, but sample time is {sample_time} \
                and older than {self.age_limit} days"
            qa_check = QACheck()
            qa_check.Title = f"Sample {context.SampleID} is missing results"
            qa_check.RunID = run_id
            qa_check.SampleID = context.SampleID
            qa_check.Severity = QACheckSeverity.Warning
            qa_check.Details = details
            qa_check.Label = "missing_results_check"
            return [qa_check]
