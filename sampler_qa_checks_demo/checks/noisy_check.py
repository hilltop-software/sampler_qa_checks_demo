import random
from datetime import datetime
from typing import List

from .i_check import ICheck
from HilltopHost.Sampler import QACheck, QACheckSeverity

class NoisyCheck(ICheck):
    """
    An simple implementation of the ICheck interface that randomly saves a critical QA check for samples.
    
    And it'll do it over and over again for the same sample, because it's noisy.
    """
    def perform_checks(self, run_id, context) -> List[QACheck]:
        if self.disabled:
            return

        x = random.random()
        if x > 0.5:
            return # 50/50 chance of not adding a QA check
                
        qa_check = QACheck()
        qa_check.Title = f"Noisy check for {context.SampleID} at {datetime.now().strftime('%y%m%d.%H%M%S.%f')[:17]}"
        qa_check.RunID = run_id
        qa_check.SampleID = context.SampleID
        qa_check.Severity = QACheckSeverity.Critical
        qa_check.Details = f"This is a NoisyCheck QA check that's randomly added to samples.\nRandom: {x}"
        qa_check.Label = "noisy_check"
        return [qa_check]
