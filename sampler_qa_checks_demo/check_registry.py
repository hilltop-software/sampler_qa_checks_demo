from typing import List, Dict, Type
from .checks.i_check import ICheck

from .checks.run_name_check import RunNameCheck
from .checks.test_check import TestCheck
from .checks.missing_results_check import MissingResultsCheck
from .checks.noisy_check import NoisyCheck
from .checks.outside_range_check import OutsideRangeCheck
from .checks.percentile_check import PercentileCheck
from .checks.threshold_check import ThresholdCheck

class CheckRegistry:
    """
    A registry that holds arrays of check classes grouped by their level:
      - run_checks
      - sample_checks
      - test_checks

    Instead of registering checks at runtime, we define them here.
    The registry also validates that each provided check class implements ICheck.
    """

    _registry: Dict[str, List[Type[ICheck]]] = {
        "run_checks": [RunNameCheck, TestCheck],
        "sample_checks": [MissingResultsCheck, NoisyCheck],
        "test_checks": [OutsideRangeCheck, PercentileCheck, ThresholdCheck],
    }

    @classmethod
    def get_checks_by_level(cls, level: str) -> List[Type[ICheck]]:
        """
        Retrieve all check classes for the given level.
        Levels might be "run_checks", "sample_checks", or "test_checks".
        Raises KeyError if the level is not found.
        """
        checks = cls._registry[level]
        # Validate that all checks implement ICheck
        for c in checks:
            if not issubclass(c, ICheck):
                raise TypeError(f"Class {c} does not implement ICheck")
        return checks
