"""
Unit tests for CheckFactory.

Tests cover:
- Factory instantiation with config and repository
- Creating check instances for each level (run, sample, test)
- Passing correct config to each check
- Handling missing config for a check
- CheckRegistry integration
"""
import pytest
from unittest.mock import Mock, MagicMock
from sampler_qa_checks_demo.check_factory import CheckFactory
from sampler_qa_checks_demo.checks.run_name_check import RunNameCheck
from sampler_qa_checks_demo.checks.demo_check import DemoCheck
from sampler_qa_checks_demo.checks.missing_results_check import MissingResultsCheck
from sampler_qa_checks_demo.checks.outside_range_check import OutsideRangeCheck


class TestCheckFactoryInitialization:
    """Tests for CheckFactory initialization."""
    
    def test_init_creates_repository(self, mock_hilltop_host, mock_pyodbc_connection):
        """Test that factory creates a Repository instance."""
        config = {"db_server": "localhost", "db_name": "Hilltop"}
        
        factory = CheckFactory(config, mock_pyodbc_connection)
        
        assert factory.config == config
        assert factory.repository is not None
    
    def test_init_with_empty_config(self, mock_hilltop_host, mock_pyodbc_connection):
        """Test initialization with empty config."""
        config = {}
        
        factory = CheckFactory(config, mock_pyodbc_connection)
        
        assert factory.config == config


class TestCheckFactoryCreateRunChecks:
    """Tests for CheckFactory.create_run_checks()."""
    
    def test_create_run_checks_returns_list(
        self, mock_hilltop_host, mock_pyodbc_connection
    ):
        """Test that create_run_checks returns a list of check instances."""
        config = {
            "RunNameCheck": {"name_max_length": 100, "disabled": False},
            "DemoCheck": {"disabled": False}
        }
        
        factory = CheckFactory(config, mock_pyodbc_connection)
        checks = factory.create_run_checks()
        
        assert isinstance(checks, list)
        assert len(checks) == 2
        assert isinstance(checks[0], RunNameCheck)
        assert isinstance(checks[1], DemoCheck)
    
    def test_create_run_checks_with_missing_config(
        self, mock_hilltop_host, mock_pyodbc_connection
    ):
        """Test that checks are created with None config when not in config dict."""
        config = {}  # No check configs
        
        factory = CheckFactory(config, mock_pyodbc_connection)
        checks = factory.create_run_checks()
        
        # Checks should still be created but with None config (disabled)
        assert len(checks) == 2
        assert checks[0].config is None
        assert checks[0].disabled is True
    
    def test_create_run_checks_passes_config_correctly(
        self, mock_hilltop_host, mock_pyodbc_connection
    ):
        """Test that correct config is passed to each check."""
        run_name_config = {"name_max_length": 50, "disabled": False}
        demo_config = {"disabled": True}
        
        config = {
            "RunNameCheck": run_name_config,
            "DemoCheck": demo_config
        }
        
        factory = CheckFactory(config, mock_pyodbc_connection)
        checks = factory.create_run_checks()
        
        # Find RunNameCheck in the list
        run_name_check = next(c for c in checks if isinstance(c, RunNameCheck))
        assert run_name_check.config == run_name_config
        assert run_name_check.name_max_length == 50
        
        # Find DemoCheck in the list
        demo_check = next(c for c in checks if isinstance(c, DemoCheck))
        assert demo_check.config == demo_config
        assert demo_check.disabled is True


class TestCheckFactoryCreateSampleChecks:
    """Tests for CheckFactory.create_sample_checks()."""
    
    def test_create_sample_checks_returns_list(
        self, mock_hilltop_host, mock_pyodbc_connection
    ):
        """Test that create_sample_checks returns a list of check instances."""
        config = {
            "MissingResultsCheck": {"age_limit": 3, "disabled": False},
            "NoisyCheck": {"disabled": False}
        }
        
        factory = CheckFactory(config, mock_pyodbc_connection)
        checks = factory.create_sample_checks()
        
        assert isinstance(checks, list)
        assert len(checks) == 2
        assert isinstance(checks[0], MissingResultsCheck)
    
    def test_create_sample_checks_passes_config_correctly(
        self, mock_hilltop_host, mock_pyodbc_connection
    ):
        """Test that correct config is passed to each check."""
        missing_results_config = {"age_limit": 5, "disabled": False}
        
        config = {
            "MissingResultsCheck": missing_results_config
        }
        
        factory = CheckFactory(config, mock_pyodbc_connection)
        checks = factory.create_sample_checks()
        
        missing_results_check = next(c for c in checks if isinstance(c, MissingResultsCheck))
        assert missing_results_check.config == missing_results_config
        assert missing_results_check.age_limit == 5


class TestCheckFactoryCreateTestChecks:
    """Tests for CheckFactory.create_test_checks()."""
    
    def test_create_test_checks_returns_list(
        self, mock_hilltop_host, mock_pyodbc_connection
    ):
        """Test that create_test_checks returns a list of check instances."""
        config = {
            "OutsideRangeCheck": {"disabled": False},
            "ThresholdCheck": {"disabled": False},
            "PercentileCheck": {"disabled": False}
        }
        
        factory = CheckFactory(config, mock_pyodbc_connection)
        checks = factory.create_test_checks()
        
        assert isinstance(checks, list)
        assert len(checks) == 3
    
    def test_create_test_checks_with_complex_config(
        self, mock_hilltop_host, mock_pyodbc_connection
    ):
        """Test test check creation with complex nested configuration."""
        config = {
            "OutsideRangeCheck": {
                "pH": {
                    "critical": {"min": 5, "max": 9},
                    "warning": {"min": 6, "max": 8}
                },
                "disabled": False
            }
        }
        
        factory = CheckFactory(config, mock_pyodbc_connection)
        checks = factory.create_test_checks()
        
        outside_range_check = next(c for c in checks if isinstance(c, OutsideRangeCheck))
        assert outside_range_check.config == config["OutsideRangeCheck"]
        assert "pH" in outside_range_check.config


class TestCheckFactoryRepositorySharing:
    """Tests that all checks share the same repository instance."""
    
    def test_all_checks_share_repository(
        self, mock_hilltop_host, mock_pyodbc_connection
    ):
        """Test that all created checks share the same repository instance."""
        config = {
            "RunNameCheck": {"disabled": False},
            "MissingResultsCheck": {"disabled": False},
            "OutsideRangeCheck": {"disabled": False}
        }
        
        factory = CheckFactory(config, mock_pyodbc_connection)
        
        run_checks = factory.create_run_checks()
        sample_checks = factory.create_sample_checks()
        test_checks = factory.create_test_checks()
        
        # All checks should have the same repository instance
        repo = factory.repository
        assert all(check.repository is repo for check in run_checks)
        assert all(check.repository is repo for check in sample_checks)
        assert all(check.repository is repo for check in test_checks)
