"""
Unit tests for CheckRegistry.

Tests cover:
- Registry structure and organization
- Getting checks by level
- ICheck interface validation
- Error handling for invalid levels
- Error handling for non-ICheck classes
"""
import pytest
from sampler_qa_checks_demo.check_registry import CheckRegistry
from sampler_qa_checks_demo.checks.i_check import ICheck
from sampler_qa_checks_demo.checks.run_name_check import RunNameCheck
from sampler_qa_checks_demo.checks.demo_check import DemoCheck
from sampler_qa_checks_demo.checks.missing_results_check import MissingResultsCheck
from sampler_qa_checks_demo.checks.noisy_check import NoisyCheck
from sampler_qa_checks_demo.checks.outside_range_check import OutsideRangeCheck
from sampler_qa_checks_demo.checks.percentile_check import PercentileCheck
from sampler_qa_checks_demo.checks.threshold_check import ThresholdCheck


class TestCheckRegistryGetChecksByLevel:
    """Tests for CheckRegistry.get_checks_by_level()."""

    def test_get_run_checks(self):
        """Test getting run-level checks."""
        checks = CheckRegistry.get_checks_by_level("run_checks")

        assert isinstance(checks, list)
        assert len(checks) == 2
        assert RunNameCheck in checks
        assert DemoCheck in checks

    def test_get_sample_checks(self):
        """Test getting sample-level checks."""
        checks = CheckRegistry.get_checks_by_level("sample_checks")

        assert isinstance(checks, list)
        assert len(checks) == 2
        assert MissingResultsCheck in checks
        assert NoisyCheck in checks

    def test_get_test_checks(self):
        """Test getting test-level checks."""
        checks = CheckRegistry.get_checks_by_level("test_checks")

        assert isinstance(checks, list)
        assert len(checks) == 3
        assert OutsideRangeCheck in checks
        assert PercentileCheck in checks
        assert ThresholdCheck in checks

    def test_invalid_level_raises_key_error(self):
        """Test that invalid level raises KeyError."""
        with pytest.raises(KeyError):
            CheckRegistry.get_checks_by_level("invalid_level")

    def test_all_checks_implement_icheck(self):
        """Test that all registered checks implement ICheck interface."""
        for level in ["run_checks", "sample_checks", "test_checks"]:
            checks = CheckRegistry.get_checks_by_level(level)
            for check_class in checks:
                assert issubclass(check_class, ICheck), \
                    f"{check_class.__name__} does not implement ICheck"


class TestCheckRegistryStructure:
    """Tests for CheckRegistry internal structure."""

    def test_registry_has_all_levels(self):
        """Test that registry contains all expected levels."""
        assert "run_checks" in CheckRegistry._registry
        assert "sample_checks" in CheckRegistry._registry
        assert "test_checks" in CheckRegistry._registry

    def test_registry_levels_are_lists(self):
        """Test that all registry levels contain lists."""
        for level, checks in CheckRegistry._registry.items():
            assert isinstance(checks, list), f"{level} is not a list"

    def test_registry_contains_no_duplicates(self):
        """Test that no check class appears twice in the same level."""
        for level, checks in CheckRegistry._registry.items():
            assert len(checks) == len(set(checks)), \
                f"{level} contains duplicate check classes"

    def test_check_not_in_multiple_levels(self):
        """Test that each check class appears in only one level."""
        all_checks = []
        for checks in CheckRegistry._registry.values():
            all_checks.extend(checks)

        # Should have no duplicates across all levels
        assert len(all_checks) == len(set(all_checks)), \
            "Some check classes appear in multiple levels"


class TestCheckRegistryValidation:
    """Tests for CheckRegistry validation logic."""

    def test_returns_class_types_not_instances(self):
        """Test that registry returns class types, not instances."""
        checks = CheckRegistry.get_checks_by_level("run_checks")

        for check in checks:
            assert isinstance(check, type), \
                f"{check} is not a class type"
            assert not isinstance(check, ICheck), \
                f"{check} is an instance, not a class"

    def test_all_check_classes_have_correct_methods(self):
        """Test that all check classes have required methods from ICheck."""
        required_methods = ["perform_checks", "has_check_result"]

        for level in ["run_checks", "sample_checks", "test_checks"]:
            checks = CheckRegistry.get_checks_by_level(level)
            for check_class in checks:
                for method in required_methods:
                    assert hasattr(check_class, method), \
                        f"{check_class.__name__} missing method {method}"
