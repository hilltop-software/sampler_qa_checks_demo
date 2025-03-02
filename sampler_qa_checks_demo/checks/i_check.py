from typing import List
import HilltopHost
from HilltopHost.Sampler import QACheck
from .. import utils

class ICheck:
    """
    Interface for all checks. Each check performs validation logic and returns a list of CheckResult objects.
    """

    def __init__(self, config, repository):
        self.config = config
        self.repository = repository
        if config is None:
            self.disabled = True
        else:
            self.disabled = config.get("disabled", False)
        if self.disabled:
            HilltopHost.LogInfo(
                f"sampler_qa_checks_demo - {self.__class__.__name__} is disabled"
            )

    def perform_checks(self, run_id, context) -> List[QACheck]:
        raise NotImplementedError("Must implement perform_checks method.")

    def has_check_result(self, context, label) -> bool:
        """
        Check if a QA check with the given label has already been performed.
        """
        if context.QAChecks is None:
            return False
        if len(context.QAChecks) == 0:
            return False
        for check in context.QAChecks:
            if check.Label == label:
                return True
        return False
