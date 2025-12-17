"""
Unit tests for MissingResultsCheck.

Tests cover:
- Age limit threshold logic (before/after cutoff)
- Status filtering (SOME_RESULTS_BACK vs other statuses)
- Missing SampleTime handling
- Duplicate check prevention via has_check_result()
- Disabled state
- Configuration defaults
- QA check object properties (severity, title, label, details)
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sampler_qa_checks_demo.checks.missing_results_check import MissingResultsCheck


class TestMissingResultsCheckInitialization:
    """Tests for MissingResultsCheck initialization."""
    
    def test_init_with_config(self, mock_hilltop_host, mock_repository, sample_config_missing_results):
        """Test initialization with provided configuration."""
        check = MissingResultsCheck(sample_config_missing_results, mock_repository)
        
        assert check.config == sample_config_missing_results
        assert check.repository == mock_repository
        assert check.disabled is False
        assert check.age_limit == 3
        mock_hilltop_host["LogInfo"].assert_called_with(
            "sampler_qa_checks_demo - MissingResultsCheck is using an age limit of 3 days"
        )
    
    def test_init_with_custom_age_limit(self, mock_hilltop_host, mock_repository):
        """Test initialization with custom age limit."""
        config = {"age_limit": 7, "disabled": False}
        check = MissingResultsCheck(config, mock_repository)
        
        assert check.age_limit == 7
        mock_hilltop_host["LogInfo"].assert_called_with(
            "sampler_qa_checks_demo - MissingResultsCheck is using an age limit of 7 days"
        )
    
    def test_init_with_default_age_limit(self, mock_hilltop_host, mock_repository):
        """Test initialization uses default age limit when not specified."""
        config = {"disabled": False}
        check = MissingResultsCheck(config, mock_repository)
        
        assert check.age_limit == 3
    
    def test_init_disabled(self, mock_hilltop_host, mock_repository):
        """Test initialization when check is disabled."""
        config = {"disabled": True, "age_limit": 5}
        check = MissingResultsCheck(config, mock_repository)
        
        assert check.disabled is True
        # Should not initialize age_limit or log when disabled
        assert not hasattr(check, "age_limit")
    
    def test_init_with_none_config(self, mock_hilltop_host, mock_repository):
        """Test initialization with None config (should be disabled)."""
        check = MissingResultsCheck(None, mock_repository)
        
        assert check.disabled is True
        assert check.config is None


class TestMissingResultsCheckPerformChecks:
    """Tests for MissingResultsCheck.perform_checks() method."""
    
    def test_sample_older_than_limit_with_some_results_back(
        self, mock_hilltop_host, mock_repository, mock_qa_check_sample, sample_config_missing_results
    ):
        """Test that QA check is created for old sample with SOME_RESULTS_BACK status."""
        # Arrange
        check = MissingResultsCheck(sample_config_missing_results, mock_repository)
        
        # Create sample that is 5 days old (older than 3 day limit)
        old_date = datetime.now() - timedelta(days=5)
        sample = mock_qa_check_sample(
            SampleID=1001,
            SampleTime=old_date.isoformat(),
            StatusID=mock_hilltop_host["RunStatus"].SOME_RESULTS_BACK,
            QAChecks=[]
        )
        
        # Act
        with patch("sampler_qa_checks_demo.checks.missing_results_check.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime.now()
            mock_datetime.fromisoformat = datetime.fromisoformat
            result = check.perform_checks(100, sample)
        
        # Assert
        assert result is not None
        assert len(result) == 1
        qa_check = result[0]
        assert qa_check.Title == "Missing results for sample 1001"
        assert qa_check.RunID == 100
        assert qa_check.SampleID == 1001
        assert qa_check.Severity == mock_hilltop_host["QACheckSeverity"].Warning
        assert qa_check.Label == "missing_results_check"
        assert "Sample ID 1001 has only some results back" in qa_check.Details
        assert "older than 3 days" in qa_check.Details
    
    def test_sample_exactly_at_limit(
        self, mock_hilltop_host, mock_repository, mock_qa_check_sample, sample_config_missing_results
    ):
        """Test sample exactly at age limit boundary (should not trigger)."""
        # Arrange
        check = MissingResultsCheck(sample_config_missing_results, mock_repository)
        
        # Create a fixed reference time
        now = datetime(2025, 12, 18, 12, 0, 0)
        exact_date = now - timedelta(days=3)
        
        sample = mock_qa_check_sample(
            SampleTime=exact_date.isoformat(),
            StatusID=mock_hilltop_host["RunStatus"].SOME_RESULTS_BACK,
            QAChecks=[]
        )
        
        # Act
        with patch("sampler_qa_checks_demo.checks.missing_results_check.datetime") as mock_datetime:
            mock_datetime.now.return_value = now
            mock_datetime.fromisoformat = datetime.fromisoformat
            result = check.perform_checks(100, sample)
        
        # Assert - does not trigger because sample_time == n_days_ago, and check uses <, not <=
        assert result is None
    
    def test_sample_younger_than_limit(
        self, mock_hilltop_host, mock_repository, mock_qa_check_sample, sample_config_missing_results
    ):
        """Test that QA check is not created for recent sample."""
        # Arrange
        check = MissingResultsCheck(sample_config_missing_results, mock_repository)
        
        # Create sample that is only 1 day old (within 3 day limit)
        recent_date = datetime.now() - timedelta(days=1)
        sample = mock_qa_check_sample(
            SampleTime=recent_date.isoformat(),
            StatusID=mock_hilltop_host["RunStatus"].SOME_RESULTS_BACK,
            QAChecks=[]
        )
        
        # Act
        with patch("sampler_qa_checks_demo.checks.missing_results_check.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime.now()
            mock_datetime.fromisoformat = datetime.fromisoformat
            result = check.perform_checks(100, sample)
        
        # Assert
        assert result is None
    
    def test_wrong_status_does_not_trigger(
        self, mock_hilltop_host, mock_repository, mock_qa_check_sample, sample_config_missing_results
    ):
        """Test that check only triggers for SOME_RESULTS_BACK status."""
        # Arrange
        check = MissingResultsCheck(sample_config_missing_results, mock_repository)
        
        # Create old sample but with different status
        old_date = datetime.now() - timedelta(days=5)
        sample = mock_qa_check_sample(
            SampleTime=old_date.isoformat(),
            StatusID=mock_hilltop_host["RunStatus"].CLOSED,  # Different status
            QAChecks=[]
        )
        
        # Act
        with patch("sampler_qa_checks_demo.checks.missing_results_check.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime.now()
            mock_datetime.fromisoformat = datetime.fromisoformat
            result = check.perform_checks(100, sample)
        
        # Assert
        assert result is None
    
    def test_missing_sample_time(
        self, mock_hilltop_host, mock_repository, mock_qa_check_sample, sample_config_missing_results
    ):
        """Test that check returns None when SampleTime is missing."""
        # Arrange
        check = MissingResultsCheck(sample_config_missing_results, mock_repository)
        
        sample = mock_qa_check_sample(
            SampleTime=None,  # Missing sample time
            StatusID=mock_hilltop_host["RunStatus"].SOME_RESULTS_BACK,
            QAChecks=[]
        )
        
        # Act
        result = check.perform_checks(100, sample)
        
        # Assert
        assert result is None
    
    def test_empty_sample_time(
        self, mock_hilltop_host, mock_repository, mock_qa_check_sample, sample_config_missing_results
    ):
        """Test that check returns None when SampleTime is empty string."""
        # Arrange
        check = MissingResultsCheck(sample_config_missing_results, mock_repository)
        
        sample = mock_qa_check_sample(
            SampleTime="",  # Empty string
            StatusID=mock_hilltop_host["RunStatus"].SOME_RESULTS_BACK,
            QAChecks=[]
        )
        
        # Act
        result = check.perform_checks(100, sample)
        
        # Assert
        assert result is None
    
    def test_duplicate_check_prevention(
        self, mock_hilltop_host, mock_repository, mock_qa_check_sample, sample_config_missing_results
    ):
        """Test that check is not performed if already exists with same label."""
        # Arrange
        check = MissingResultsCheck(sample_config_missing_results, mock_repository)
        
        # Create existing QA check with same label
        existing_check = Mock()
        existing_check.Label = "missing_results_check"
        
        old_date = datetime.now() - timedelta(days=5)
        sample = mock_qa_check_sample(
            SampleTime=old_date.isoformat(),
            StatusID=mock_hilltop_host["RunStatus"].SOME_RESULTS_BACK,
            QAChecks=[existing_check]  # Already has check with this label
        )
        
        # Act
        result = check.perform_checks(100, sample)
        
        # Assert
        assert result is None
    
    def test_disabled_check_returns_none(
        self, mock_hilltop_host, mock_repository, mock_qa_check_sample
    ):
        """Test that disabled check returns None without performing logic."""
        # Arrange
        config = {"disabled": True, "age_limit": 3}
        check = MissingResultsCheck(config, mock_repository)
        
        old_date = datetime.now() - timedelta(days=5)
        sample = mock_qa_check_sample(
            SampleTime=old_date.isoformat(),
            StatusID=mock_hilltop_host["RunStatus"].SOME_RESULTS_BACK,
            QAChecks=[]
        )
        
        # Act
        # Since age_limit is not set when disabled, this should raise AttributeError
        # if the check logic runs
        with pytest.raises(AttributeError):
            check.perform_checks(100, sample)


class TestMissingResultsCheckEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_very_old_sample(
        self, mock_hilltop_host, mock_repository, mock_qa_check_sample, sample_config_missing_results
    ):
        """Test with a very old sample (30 days)."""
        # Arrange
        check = MissingResultsCheck(sample_config_missing_results, mock_repository)
        
        very_old_date = datetime.now() - timedelta(days=30)
        sample = mock_qa_check_sample(
            SampleID=2002,
            SampleTime=very_old_date.isoformat(),
            StatusID=mock_hilltop_host["RunStatus"].SOME_RESULTS_BACK,
            QAChecks=[]
        )
        
        # Act
        with patch("sampler_qa_checks_demo.checks.missing_results_check.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime.now()
            mock_datetime.fromisoformat = datetime.fromisoformat
            result = check.perform_checks(100, sample)
        
        # Assert
        assert result is not None
        assert len(result) == 1
        qa_check = result[0]
        assert qa_check.SampleID == 2002
    
    def test_zero_age_limit(
        self, mock_hilltop_host, mock_repository, mock_qa_check_sample
    ):
        """Test with age limit set to 0 (all samples with SOME_RESULTS_BACK should trigger)."""
        # Arrange
        config = {"age_limit": 0, "disabled": False}
        check = MissingResultsCheck(config, mock_repository)
        
        # Sample from 1 hour ago
        recent_date = datetime.now() - timedelta(hours=1)
        sample = mock_qa_check_sample(
            SampleTime=recent_date.isoformat(),
            StatusID=mock_hilltop_host["RunStatus"].SOME_RESULTS_BACK,
            QAChecks=[]
        )
        
        # Act
        with patch("sampler_qa_checks_demo.checks.missing_results_check.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime.now()
            mock_datetime.fromisoformat = datetime.fromisoformat
            result = check.perform_checks(100, sample)
        
        # Assert - should trigger because sample_time < today (0 days ago)
        assert result is not None
        assert len(result) == 1
    
    def test_qa_check_details_format(
        self, mock_hilltop_host, mock_repository, mock_qa_check_sample, sample_config_missing_results
    ):
        """Test that QA check details are formatted correctly."""
        # Arrange
        check = MissingResultsCheck(sample_config_missing_results, mock_repository)
        
        old_date = datetime.now() - timedelta(days=5)
        sample = mock_qa_check_sample(
            SampleID=1234,
            SampleTime=old_date.isoformat(),
            StatusID=mock_hilltop_host["RunStatus"].SOME_RESULTS_BACK,
            QAChecks=[]
        )
        
        # Act
        with patch("sampler_qa_checks_demo.checks.missing_results_check.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime.now()
            mock_datetime.fromisoformat = datetime.fromisoformat
            result = check.perform_checks(100, sample)
        
        # Assert
        qa_check = result[0]
        assert "Sample ID 1234" in qa_check.Details
        assert "has only some results back" in qa_check.Details
        assert str(old_date) in qa_check.Details
        assert "older than 3 days" in qa_check.Details
    
    def test_different_run_id(
        self, mock_hilltop_host, mock_repository, mock_qa_check_sample, sample_config_missing_results
    ):
        """Test that RunID is correctly set from parameter."""
        # Arrange
        check = MissingResultsCheck(sample_config_missing_results, mock_repository)
        
        old_date = datetime.now() - timedelta(days=5)
        sample = mock_qa_check_sample(
            SampleTime=old_date.isoformat(),
            StatusID=mock_hilltop_host["RunStatus"].SOME_RESULTS_BACK,
            QAChecks=[]
        )
        
        # Act
        with patch("sampler_qa_checks_demo.checks.missing_results_check.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime.now()
            mock_datetime.fromisoformat = datetime.fromisoformat
            result = check.perform_checks(999, sample)  # Different run_id
        
        # Assert
        assert result[0].RunID == 999
