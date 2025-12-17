"""
Shared pytest fixtures and mocks for Sampler QA Checks testing.
"""
import sys
from unittest.mock import Mock, MagicMock
from datetime import datetime

# Mock HilltopHost module before any imports
if 'HilltopHost' not in sys.modules:
    mock_hilltop_host_module = MagicMock()

    # Mock RunStatus enum
    mock_run_status = Mock()
    mock_run_status.SOME_RESULTS_BACK = 3
    mock_run_status.CANCELLED = 5
    mock_run_status.CLOSED = 6
    mock_hilltop_host_module.RunStatus = mock_run_status

    # Mock Sampler submodule
    mock_sampler = MagicMock()

    # Mock QACheckSeverity enum
    mock_severity = Mock()
    mock_severity.OK = 0
    mock_severity.Information = 1
    mock_severity.Warning = 2
    mock_severity.Critical = 3
    mock_sampler.QACheckSeverity = mock_severity

    # Mock QACheck class
    class MockQACheck:
        def __init__(self):
            self.Title = ""
            self.RunID = 0
            self.SampleID = 0
            self.LabTestID = 0
            self.Severity = 0
            self.Details = ""
            self.Label = ""

    mock_sampler.QACheck = MockQACheck
    mock_sampler.SaveQACheck = Mock()

    mock_hilltop_host_module.Sampler = mock_sampler

    # Mock System submodule
    mock_system = MagicMock()
    mock_system.GetConfigSection = Mock(return_value=None)
    mock_hilltop_host_module.System = mock_system

    # Mock logging functions
    mock_hilltop_host_module.LogInfo = Mock()
    mock_hilltop_host_module.LogWarning = Mock()
    mock_hilltop_host_module.LogError = Mock()
    mock_hilltop_host_module.LogDebug = Mock()

    sys.modules['HilltopHost'] = mock_hilltop_host_module
    sys.modules['HilltopHost.Sampler'] = mock_sampler
    sys.modules['HilltopHost.System'] = mock_system

import pytest


@pytest.fixture
def mock_hilltop_host(monkeypatch):
    """Mock all HilltopHost functions and classes."""
    # Mock logging functions
    mock_log_info = Mock()
    mock_log_warning = Mock()
    mock_log_error = Mock()
    mock_log_debug = Mock()

    monkeypatch.setattr("HilltopHost.LogInfo", mock_log_info)
    monkeypatch.setattr("HilltopHost.LogWarning", mock_log_warning)
    monkeypatch.setattr("HilltopHost.LogError", mock_log_error)
    monkeypatch.setattr("HilltopHost.LogDebug", mock_log_debug)

    # Mock RunStatus enum
    mock_run_status = Mock()
    mock_run_status.SOME_RESULTS_BACK = 3
    mock_run_status.CANCELLED = 5
    mock_run_status.CLOSED = 6
    monkeypatch.setattr("HilltopHost.RunStatus", mock_run_status)

    # Mock QACheckSeverity enum
    mock_severity = Mock()
    mock_severity.OK = 0
    mock_severity.Information = 1
    mock_severity.Warning = 2
    mock_severity.Critical = 3
    monkeypatch.setattr("HilltopHost.Sampler.QACheckSeverity", mock_severity)

    # Mock SaveQACheck function
    mock_save_qa_check = Mock()
    monkeypatch.setattr("HilltopHost.Sampler.SaveQACheck", mock_save_qa_check)

    return {
        "LogInfo": mock_log_info,
        "LogWarning": mock_log_warning,
        "LogError": mock_log_error,
        "LogDebug": mock_log_debug,
        "RunStatus": mock_run_status,
        "QACheckSeverity": mock_severity,
        "SaveQACheck": mock_save_qa_check,
    }


@pytest.fixture
def mock_qa_check():
    """Factory fixture to create mock QACheck objects."""
    def _create_qa_check(**kwargs):
        check = Mock()
        check.Title = kwargs.get("Title", "")
        check.RunID = kwargs.get("RunID", 0)
        check.SampleID = kwargs.get("SampleID", 0)
        check.LabTestID = kwargs.get("LabTestID", 0)
        check.Severity = kwargs.get("Severity", 0)
        check.Details = kwargs.get("Details", "")
        check.Label = kwargs.get("Label", "")
        return check
    return _create_qa_check


@pytest.fixture
def mock_qa_check_sample():
    """Factory fixture to create mock QACheckSample objects."""
    def _create_sample(**kwargs):
        sample = Mock()
        sample.SampleID = kwargs.get("SampleID", 1001)
        sample.SiteName = kwargs.get("SiteName", "Test Site")
        sample.SampleTime = kwargs.get("SampleTime", "2025-12-15T10:30:00")
        sample.RunID = kwargs.get("RunID", 100)
        sample.StatusID = kwargs.get("StatusID", 3)  # SOME_RESULTS_BACK
        sample.Username = kwargs.get("Username", "testuser")
        sample.SampleCost = kwargs.get("SampleCost", 0.0)
        sample.HasFieldData = kwargs.get("HasFieldData", False)
        sample.SampleTypeCode = kwargs.get("SampleTypeCode", "W")
        sample.Tests = kwargs.get("Tests", [])
        sample.QAChecks = kwargs.get("QAChecks", [])
        return sample
    return _create_sample


@pytest.fixture
def mock_qa_check_lab_test():
    """Factory fixture to create mock QACheckLabTest objects."""
    def _create_lab_test(**kwargs):
        test = Mock()
        test.LabTestID = kwargs.get("LabTestID", 2001)
        test.SampleID = kwargs.get("SampleID", 1001)
        test.IsTestSet = kwargs.get("IsTestSet", False)
        test.Tests = kwargs.get("Tests", [])
        test.QAChecks = kwargs.get("QAChecks", [])

        # Mock Result object
        result = Mock()
        result.TestValue = kwargs.get("TestValue", "7.5")
        test.Result = result

        return test
    return _create_lab_test


@pytest.fixture
def mock_qa_check_run():
    """Factory fixture to create mock QACheckRun objects."""
    def _create_run(**kwargs):
        run = Mock()
        run.RunID = kwargs.get("RunID", 100)
        run.RunName = kwargs.get("RunName", "Test Run")
        run.Samples = kwargs.get("Samples", [])
        run.QAChecks = kwargs.get("QAChecks", [])
        return run
    return _create_run


@pytest.fixture
def mock_repository():
    """Mock Repository object."""
    repo = Mock()
    repo.get_measurement_by_lab_test_id = Mock(return_value=None)
    repo.get_sample_metadata = Mock(return_value=None)
    return repo


@pytest.fixture
def mock_pyodbc_connection():
    """Mock pyodbc database connection."""
    conn = Mock()
    cursor = Mock()
    cursor.fetchone = Mock(return_value=("SQL Server version",))
    cursor.fetchall = Mock(return_value=[])
    cursor.execute = Mock()
    cursor.close = Mock()
    conn.cursor = Mock(return_value=cursor)
    conn.close = Mock()
    return conn


@pytest.fixture
def sample_config_missing_results():
    """Sample configuration for MissingResultsCheck."""
    return {
        "age_limit": 3,
        "disabled": False,
    }


@pytest.fixture
def sample_config_run_name():
    """Sample configuration for RunNameCheck."""
    return {
        "name_max_length": 100,
        "disabled": False,
    }


@pytest.fixture
def sample_config_outside_range():
    """Sample configuration for OutsideRangeCheck."""
    return {
        "pH": {
            "critical": {
                "min": 5,
                "max": 9,
            },
            "warning": {
                "min": 6,
                "max": 8,
            },
        },
        "disabled": False,
    }


@pytest.fixture
def sample_config_threshold():
    """Sample configuration for ThresholdCheck."""
    return {
        "Nitrate - Nitrogen": {
            "Information": 1.0,
            "Warning": 3.0,
            "Critical": 10.0,
        },
        "disabled": False,
    }


@pytest.fixture
def sample_config_percentile():
    """Sample configuration for PercentileCheck."""
    return {
        "data_file": "C:\\Hilltop\\Data\\Archive.hts",
        "min_data_points": 20,
        "period_years": 10,
        "pH": {
            "critical": "5,95",
            "warning": "10,90",
        },
        "disabled": False,
    }


@pytest.fixture
def mock_hilltop_module(monkeypatch):
    """Mock the Hilltop Python module."""
    mock_hilltop = Mock()

    # Mock Connect/Disconnect
    mock_dfile = Mock()
    mock_hilltop.Connect = Mock(return_value=mock_dfile)
    mock_hilltop.Disconnect = Mock()

    # Mock GetData
    mock_series = Mock()
    mock_series.Values = []
    mock_hilltop.GetData = Mock(return_value=mock_series)

    # Mock PDist
    mock_hilltop.PDist = Mock(return_value=([], []))

    monkeypatch.setattr("Hilltop.Connect", mock_hilltop.Connect)
    monkeypatch.setattr("Hilltop.Disconnect", mock_hilltop.Disconnect)
    monkeypatch.setattr("Hilltop.GetData", mock_hilltop.GetData)
    monkeypatch.setattr("Hilltop.PDist", mock_hilltop.PDist)

    return mock_hilltop


@pytest.fixture
def freeze_time(monkeypatch):
    """Fixture to freeze datetime.now() to a specific date."""
    def _freeze(frozen_datetime):
        class FrozenDateTime:
            @staticmethod
            def now():
                return frozen_datetime

            @staticmethod
            def fromisoformat(date_string):
                return datetime.fromisoformat(date_string)

        monkeypatch.setattr("datetime.datetime", FrozenDateTime)
        return frozen_datetime

    return _freeze
