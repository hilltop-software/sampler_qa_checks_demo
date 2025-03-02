from typing import List
from .checks.i_check import ICheck
from .check_registry import CheckRegistry
from .repository import Repository

class CheckFactory:
    """
    Factory that creates check instances based on configuration in CheckRegistry.

    The factory uses CheckRegistry to get all available checks for a level,
    then filters them by the names listed in the configuration.
    """
    def __init__(self, config: dict, connection):
        self.config = config
        self.repository = Repository(connection)

    def create_run_checks(self) -> List[ICheck]:
        return self._create_checks("run_checks")

    def create_sample_checks(self) -> List[ICheck]:
        return self._create_checks("sample_checks")

    def create_test_checks(self) -> List[ICheck]:
        return self._create_checks("test_checks")

    def _create_checks(self, level: str) -> List[ICheck]:
        # Retrieve all available checks for the requested level
        available_check_classes = CheckRegistry.get_checks_by_level(level)
        instantiated_checks = []
        for check_class in available_check_classes:
            # Get the class name to use as the key for the configuration block
            class_name = check_class.__name__
            class_config = self.config.get(class_name, {})
            instantiated_checks.append(check_class(class_config, self.repository))
        return instantiated_checks