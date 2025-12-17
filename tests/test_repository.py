"""
Unit tests for Repository.

Tests cover:
- get_sample_metadata query execution and result mapping
- get_measurement_by_lab_test_id query execution and result mapping
- Error handling and logging
- Database connection usage
- None return when no data found
"""
import pytest
from unittest.mock import Mock, MagicMock
from sampler_qa_checks_demo.repository import Repository


class TestRepositoryInitialization:
    """Tests for Repository initialization."""
    
    def test_init_with_connection(self, mock_pyodbc_connection):
        """Test initialization with database connection."""
        repo = Repository(mock_pyodbc_connection)
        
        assert repo.connection == mock_pyodbc_connection


class TestRepositoryGetSampleMetadata:
    """Tests for Repository.get_sample_metadata()."""
    
    def test_get_sample_metadata_success(self, mock_hilltop_host, mock_pyodbc_connection):
        """Test successful retrieval of sample metadata."""
        # Arrange
        mock_cursor = Mock()
        mock_row = (
            "TestLab",  # LabName
            "pH Test",  # TestName
            "pH",  # MeasurementName
            "",  # Units
            1,  # Divisor
            "7.5",  # TestValue
            1001,  # SampleID
            5001,  # SiteID
            "Test Site",  # SiteName
            100,  # RunID
            "Test Run",  # RunName
            "2025-12-01",  # RunDate
            "W",  # SampleTypeCode
            200,  # ProjectID
            "Test Project",  # ProjectName
            None,  # SampleInfo
            "<Test ID='2001'/>",  # TestInfo
            2001,  # TestID
            "Lab pH",  # LabTestName
            "Method A",  # LabMethod
            2001  # LabTestID
        )
        
        mock_cursor.fetchone.return_value = mock_row
        mock_cursor.description = [
            ("LabName",), ("TestName",), ("MeasurementName",), ("Units",),
            ("Divisor",), ("TestValue",), ("SampleID",), ("SiteID",),
            ("SiteName",), ("RunID",), ("RunName",), ("RunDate",),
            ("SampleTypeCode",), ("ProjectID",), ("ProjectName",),
            ("SampleInfo",), ("TestInfo",), ("TestID",),
            ("LabTestName",), ("LabMethod",), ("LabTestID",)
        ]
        
        mock_pyodbc_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_pyodbc_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        repo = Repository(mock_pyodbc_connection)
        
        # Act
        result = repo.get_sample_metadata(1001, 2001)
        
        # Assert
        assert result is not None
        assert result["LabName"] == "TestLab"
        assert result["TestName"] == "pH Test"
        assert result["MeasurementName"] == "pH"
        assert result["TestValue"] == "7.5"
        assert result["SampleID"] == 1001
        assert result["RunID"] == 100
        
        mock_cursor.execute.assert_called_once()
        assert mock_cursor.execute.call_args[0][1] == 1001
        assert mock_cursor.execute.call_args[0][2] == 2001
    
    def test_get_sample_metadata_not_found(self, mock_hilltop_host, mock_pyodbc_connection):
        """Test when sample metadata is not found."""
        # Arrange
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        
        mock_pyodbc_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_pyodbc_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        repo = Repository(mock_pyodbc_connection)
        
        # Act
        result = repo.get_sample_metadata(9999, 9999)
        
        # Assert
        assert result is None
    
    def test_get_sample_metadata_error_handling(self, mock_hilltop_host, mock_pyodbc_connection):
        """Test error handling when database query fails."""
        # Arrange
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("Database error")
        
        mock_pyodbc_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_pyodbc_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        repo = Repository(mock_pyodbc_connection)
        
        # Act
        result = repo.get_sample_metadata(1001, 2001)
        
        # Assert
        assert result is None
        mock_hilltop_host["LogError"].assert_called_once()
        assert "Database error" in mock_hilltop_host["LogError"].call_args[0][0]


class TestRepositoryGetMeasurementByLabTestId:
    """Tests for Repository.get_measurement_by_lab_test_id()."""
    
    def test_get_measurement_success(self, mock_hilltop_host, mock_pyodbc_connection):
        """Test successful retrieval of measurement by lab test ID."""
        # Arrange
        mock_cursor = Mock()
        mock_row = (
            "Lab pH",  # LabTestName
            "Method A",  # LabMethod
            2001,  # LabTestID
            "TestLab",  # LabName
            "pH Test",  # TestName
            "pH"  # MeasurementName
        )
        
        mock_cursor.fetchone.return_value = mock_row
        mock_cursor.description = [
            ("LabTestName",), ("LabMethod",), ("LabTestID",),
            ("LabName",), ("TestName",), ("MeasurementName",)
        ]
        
        mock_pyodbc_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_pyodbc_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        repo = Repository(mock_pyodbc_connection)
        
        # Act
        result = repo.get_measurement_by_lab_test_id(2001)
        
        # Assert
        assert result is not None
        assert result["LabTestName"] == "Lab pH"
        assert result["LabMethod"] == "Method A"
        assert result["LabTestID"] == 2001
        assert result["LabName"] == "TestLab"
        assert result["TestName"] == "pH Test"
        assert result["MeasurementName"] == "pH"
        
        mock_cursor.execute.assert_called_once()
        assert mock_cursor.execute.call_args[0][1] == 2001
    
    def test_get_measurement_not_found(self, mock_hilltop_host, mock_pyodbc_connection):
        """Test when measurement is not found."""
        # Arrange
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        
        mock_pyodbc_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_pyodbc_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        repo = Repository(mock_pyodbc_connection)
        
        # Act
        result = repo.get_measurement_by_lab_test_id(9999)
        
        # Assert
        assert result is None
    
    def test_get_measurement_error_handling(self, mock_hilltop_host, mock_pyodbc_connection):
        """Test error handling when database query fails."""
        # Arrange
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = Exception("Connection timeout")
        
        mock_pyodbc_connection.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_pyodbc_connection.cursor.return_value.__exit__ = Mock(return_value=False)
        
        repo = Repository(mock_pyodbc_connection)
        
        # Act
        result = repo.get_measurement_by_lab_test_id(2001)
        
        # Assert
        assert result is None
        mock_hilltop_host["LogError"].assert_called_once()
        assert "Connection timeout" in mock_hilltop_host["LogError"].call_args[0][0]


class TestRepositoryCursorManagement:
    """Tests for proper cursor and connection management."""
    
    def test_cursor_context_manager_used(self, mock_hilltop_host, mock_pyodbc_connection):
        """Test that cursor is used as context manager."""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = mock_cursor
        mock_pyodbc_connection.cursor.return_value = mock_context_manager
        
        repo = Repository(mock_pyodbc_connection)
        repo.get_measurement_by_lab_test_id(2001)
        
        # Verify context manager was used
        mock_context_manager.__enter__.assert_called_once()
        mock_context_manager.__exit__.assert_called_once()
