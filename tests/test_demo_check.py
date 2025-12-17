"""
Unit tests for DemoCheck.

Tests cover:
- Always creates OK severity check
- Duplicate check prevention
- Logging behavior
- QA check properties
"""
import pytest
from unittest.mock import Mock
from sampler_qa_checks_demo.checks.demo_check import DemoCheck


class TestDemoCheckInitialization:
    """Tests for DemoCheck initialization."""
    
    def test_init_with_config(self, mock_hilltop_host, mock_repository):
        """Test initialization with provided configuration."""
        config = {"disabled": False}
        check = DemoCheck(config, mock_repository)
        
        assert check.config == config
        assert check.repository == mock_repository
        assert check.disabled is False
    
    def test_init_disabled(self, mock_hilltop_host, mock_repository):
        """Test initialization when check is disabled."""
        config = {"disabled": True}
        check = DemoCheck(config, mock_repository)
        
        assert check.disabled is True
    
    def test_init_with_none_config(self, mock_hilltop_host, mock_repository):
        """Test initialization with None config (should be disabled)."""
        check = DemoCheck(None, mock_repository)
        
        assert check.disabled is True


class TestDemoCheckPerformChecks:
    """Tests for DemoCheck.perform_checks() method."""
    
    def test_creates_ok_check(
        self, mock_hilltop_host, mock_repository, mock_qa_check_run
    ):
        """Test that check always creates an OK severity QA check."""
        # Arrange
        config = {"disabled": False}
        check = DemoCheck(config, mock_repository)
        
        run = mock_qa_check_run(
            RunID=100,
            QAChecks=[]
        )
        
        # Act
        result = check.perform_checks(100, run)
        
        # Assert
        assert result is not None
        assert len(result) == 1
        qa_check = result[0]
        assert qa_check.Title == "Demo Check"
        assert qa_check.RunID == 100
        assert qa_check.Severity == mock_hilltop_host["QACheckSeverity"].OK
        assert qa_check.Label == "demo_check"
        
        # Verify logging
        mock_hilltop_host["LogInfo"].assert_any_call(
            "sampler_qa_checks_demo - DemoCheck called"
        )
    
    def test_duplicate_check_prevention(
        self, mock_hilltop_host, mock_repository, mock_qa_check_run
    ):
        """Test that check is not performed if already exists with same label."""
        # Arrange
        config = {"disabled": False}
        check = DemoCheck(config, mock_repository)
        
        existing_check = Mock()
        existing_check.Label = "demo_check"
        
        run = mock_qa_check_run(
            RunID=100,
            QAChecks=[existing_check]
        )
        
        # Act
        result = check.perform_checks(100, run)
        
        # Assert
        assert result is None
    
    def test_different_run_id(
        self, mock_hilltop_host, mock_repository, mock_qa_check_run
    ):
        """Test that RunID is correctly set from parameter."""
        # Arrange
        config = {"disabled": False}
        check = DemoCheck(config, mock_repository)
        
        run = mock_qa_check_run(QAChecks=[])
        
        # Act
        result = check.perform_checks(999, run)
        
        # Assert
        assert result[0].RunID == 999
    
    def test_multiple_invocations(
        self, mock_hilltop_host, mock_repository, mock_qa_check_run
    ):
        """Test that check can be called multiple times for different runs."""
        # Arrange
        config = {"disabled": False}
        check = DemoCheck(config, mock_repository)
        
        run1 = mock_qa_check_run(RunID=100, QAChecks=[])
        run2 = mock_qa_check_run(RunID=200, QAChecks=[])
        
        # Act
        result1 = check.perform_checks(100, run1)
        result2 = check.perform_checks(200, run2)
        
        # Assert
        assert result1[0].RunID == 100
        assert result2[0].RunID == 200
        assert mock_hilltop_host["LogInfo"].call_count >= 2
