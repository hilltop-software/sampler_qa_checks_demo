from typing import List, Dict, Type
from .checks.i_check import ICheck

# from .checks.simple_check import SimpleCheck
from .checks.run_name_check import RunNameCheck
from .checks.sample_time_check import SampleTimeCheck
from .checks.noisy_check import NoisyCheck
from .checks.outside_range_check import OutsideRangeCheck
from .checks.percentile_check import PercentileCheck

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
        "run_checks": [RunNameCheck],
        "sample_checks": [SampleTimeCheck, NoisyCheck],
        "test_checks": [OutsideRangeCheck, PercentileCheck],
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
