from typing import List
import HilltopHost
from HilltopHost.Sampler import QACheck
from sampler_qa_checks_demo.repository import Repository


class ICheck:
    """
    Interface for all checks. Each check performs validation logic and returns a list of CheckResult objects.
    """

    def __init__(self, config : dict, repository: Repository):
        """
        Initializes the check with the given configuration and repository.

        Args:
            config (dict): Configuration settings.
            repository (Repository): The data repository.
        """
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

    def perform_checks(self, run_id : int, context) -> List[QACheck]:
        """
        Perform checks on the given context (run, sample, or test) and return a list of QA checks.

        Args:
            run_id: The ID of the run
            context: The object to check (run, sample, or test)

        Returns:
            A list of QACheck objects, or None if no checks were triggered
        """
        raise NotImplementedError("Must implement perform_checks method.")

    def has_check_result(self, context, label) -> bool:
        """
        Checks if the context has a check result with the specified label.

        Args:
            context: The context object containing QAChecks.
            label: The label to look for.

        Returns:
            bool: True if the specified label is found, otherwise False.
        """
        if context.QAChecks is None:
            return False

        if len(context.QAChecks) == 0:
            return False

        for check in context.QAChecks:
            if check.Label == label:
                return True
        return False
