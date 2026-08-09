"""
Unit tests for RunNameCheck.

Tests cover:
- Name length validation against max length
- Exact boundary testing (at limit, over limit)
- Duplicate check prevention
- Disabled state
- Configuration defaults
- QA check properties
"""
from unittest.mock import Mock
from sampler_qa_checks_demo.checks.run_name_check import RunNameCheck


class TestRunNameCheckInitialization:
    """Tests for RunNameCheck initialization."""

    def test_init_with_config(self, mock_hilltop_host, mock_repository, sample_config_run_name):
        """Test initialization with provided configuration."""
        check = RunNameCheck(sample_config_run_name, mock_repository)

        assert check.config == sample_config_run_name
        assert check.repository == mock_repository
        assert check.disabled is False
        assert check.name_max_length == 100
        mock_hilltop_host["LogInfo"].assert_called_with(
            "sampler_qa_checks_demo - RunNameCheck is using a limit of 100 characters"
        )

    def test_init_with_custom_length(self, mock_hilltop_host, mock_repository):
        """Test initialization with custom max length."""
        config = {"name_max_length": 50, "disabled": False}
        check = RunNameCheck(config, mock_repository)

        assert check.name_max_length == 50
        mock_hilltop_host["LogInfo"].assert_called_with(
            "sampler_qa_checks_demo - RunNameCheck is using a limit of 50 characters"
        )

    def test_init_with_default_length(self, mock_hilltop_host, mock_repository):
        """Test initialization uses default length when not specified."""
        config = {"disabled": False}
        check = RunNameCheck(config, mock_repository)

        assert check.name_max_length == 100

    def test_init_disabled(self, mock_hilltop_host, mock_repository):
        """Test initialization when check is disabled."""
        config = {"disabled": True, "name_max_length": 50}
        check = RunNameCheck(config, mock_repository)

        assert check.disabled is True
        assert not hasattr(check, "name_max_length")

    def test_init_with_none_config(self, mock_hilltop_host, mock_repository):
        """Test initialization with None config (should be disabled)."""
        check = RunNameCheck(None, mock_repository)

        assert check.disabled is True
        assert check.config is None


class TestRunNameCheckPerformChecks:
    """Tests for RunNameCheck.perform_checks() method."""

    def test_run_name_exceeds_limit(
        self, mock_hilltop_host, mock_repository, mock_qa_check_run, sample_config_run_name
    ):
        """Test that QA check is created when run name exceeds limit."""
        # Arrange
        check = RunNameCheck(sample_config_run_name, mock_repository)

        long_name = "A" * 150  # 150 characters, exceeds 100
        run = mock_qa_check_run(
            RunID=100,
            RunName=long_name,
            QAChecks=[]
        )

        # Act
        result = check.perform_checks(100, run)

        # Assert
        assert result is not None
        assert len(result) == 1
        qa_check = result[0]
        assert qa_check.Title == "Run name is too long"
        assert qa_check.RunID == 100
        assert qa_check.Severity == mock_hilltop_host["QACheckSeverity"].Information
        assert qa_check.Label == "run_name_check"
        assert long_name in qa_check.Details
        assert "150 characters long" in qa_check.Details
        assert "maximum of 100" in qa_check.Details

    def test_run_name_at_exact_limit(
        self, mock_hilltop_host, mock_repository, mock_qa_check_run, sample_config_run_name
    ):
        """Test run name exactly at limit does not trigger."""
        # Arrange
        check = RunNameCheck(sample_config_run_name, mock_repository)

        exact_name = "A" * 100  # Exactly 100 characters
        run = mock_qa_check_run(
            RunName=exact_name,
            QAChecks=[]
        )

        # Act
        result = check.perform_checks(100, run)

        # Assert
        assert result is None

    def test_run_name_one_over_limit(
        self, mock_hilltop_host, mock_repository, mock_qa_check_run, sample_config_run_name
    ):
        """Test run name one character over limit triggers."""
        # Arrange
        check = RunNameCheck(sample_config_run_name, mock_repository)

        over_name = "A" * 101  # 101 characters
        run = mock_qa_check_run(
            RunName=over_name,
            QAChecks=[]
        )

        # Act
        result = check.perform_checks(100, run)

        # Assert
        assert result is not None
        assert len(result) == 1
        assert "101 characters long" in result[0].Details

    def test_run_name_under_limit(
        self, mock_hilltop_host, mock_repository, mock_qa_check_run, sample_config_run_name
    ):
        """Test that QA check is not created when run name is under limit."""
        # Arrange
        check = RunNameCheck(sample_config_run_name, mock_repository)

        short_name = "Short Run Name"
        run = mock_qa_check_run(
            RunName=short_name,
            QAChecks=[]
        )

        # Act
        result = check.perform_checks(100, run)

        # Assert
        assert result is None

    def test_empty_run_name(
        self, mock_hilltop_host, mock_repository, mock_qa_check_run, sample_config_run_name
    ):
        """Test empty run name does not trigger."""
        # Arrange
        check = RunNameCheck(sample_config_run_name, mock_repository)

        run = mock_qa_check_run(
            RunName="",
            QAChecks=[]
        )

        # Act
        result = check.perform_checks(100, run)

        # Assert
        assert result is None

    def test_duplicate_check_prevention(
        self, mock_hilltop_host, mock_repository, mock_qa_check_run, sample_config_run_name
    ):
        """Test that check is not performed if already exists with same label."""
        # Arrange
        check = RunNameCheck(sample_config_run_name, mock_repository)

        existing_check = Mock()
        existing_check.Label = "run_name_check"

        long_name = "A" * 150
        run = mock_qa_check_run(
            RunName=long_name,
            QAChecks=[existing_check]
        )

        # Act
        result = check.perform_checks(100, run)

        # Assert
        assert result is None

    def test_custom_max_length(
        self, mock_hilltop_host, mock_repository, mock_qa_check_run
    ):
        """Test with custom max length configuration."""
        # Arrange
        config = {"name_max_length": 20, "disabled": False}
        check = RunNameCheck(config, mock_repository)

        run = mock_qa_check_run(
            RunName="This is a long run name",  # 23 characters
            QAChecks=[]
        )

        # Act
        result = check.perform_checks(100, run)

        # Assert
        assert result is not None
        assert "23 characters long" in result[0].Details
        assert "maximum of 20" in result[0].Details

    def test_different_run_id(
        self, mock_hilltop_host, mock_repository, mock_qa_check_run, sample_config_run_name
    ):
        """Test that RunID is correctly set from parameter."""
        # Arrange
        check = RunNameCheck(sample_config_run_name, mock_repository)

        run = mock_qa_check_run(
            RunName="A" * 150,
            QAChecks=[]
        )

        # Act
        result = check.perform_checks(999, run)

        # Assert
        assert result[0].RunID == 999
