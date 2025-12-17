"""
Unit tests for ConfigLoader.

Tests cover:
- Loading valid YAML configuration
- Error handling for missing config section
- Error handling for missing ConfigFile key
- Error handling for non-existent file
- YAML parsing
"""
import pytest
from unittest.mock import Mock, patch, mock_open
from sampler_qa_checks_demo.config_loader import ConfigLoader


class TestConfigLoaderLoad:
    """Tests for ConfigLoader.load() method."""
    
    def test_load_valid_config(self, mock_hilltop_host, tmp_path):
        """Test loading a valid YAML configuration file."""
        # Create a temporary config file
        config_file = tmp_path / "test_config.yaml"
        config_content = """
db_server: localhost
db_name: Hilltop
save_qachecks_to_database: false
RunNameCheck:
  name_max_length: 100
MissingResultsCheck:
  age_limit: 3
"""
        config_file.write_text(config_content)
        
        # Mock GetConfigSection to return path to temp file
        mock_get_config = Mock(return_value={"ConfigFile": str(config_file)})
        
        with patch("HilltopHost.System.GetConfigSection", mock_get_config):
            config = ConfigLoader.load()
        
        assert config["db_server"] == "localhost"
        assert config["db_name"] == "Hilltop"
        assert config["save_qachecks_to_database"] is False
        assert config["RunNameCheck"]["name_max_length"] == 100
        assert config["MissingResultsCheck"]["age_limit"] == 3
        
        mock_hilltop_host["LogInfo"].assert_called_with(
            f"sampler_qa_checks_demo - using configuration file from {str(config_file)}"
        )
    
    def test_load_missing_config_section(self, mock_hilltop_host):
        """Test error when config section is not found."""
        mock_get_config = Mock(return_value=None)
        
        with patch("HilltopHost.System.GetConfigSection", mock_get_config):
            with pytest.raises(ValueError, match="configuration section not found"):
                ConfigLoader.load()
    
    def test_load_empty_config_section(self, mock_hilltop_host):
        """Test error when config section is empty dict."""
        mock_get_config = Mock(return_value={})
        
        with patch("HilltopHost.System.GetConfigSection", mock_get_config):
            # Empty dict is falsy in Python, so it raises "configuration section not found"
            with pytest.raises(ValueError, match="configuration section not found"):
                ConfigLoader.load()
    
    def test_load_missing_config_file_key(self, mock_hilltop_host):
        """Test error when ConfigFile key is missing."""
        mock_get_config = Mock(return_value={"OtherKey": "value"})
        
        with patch("HilltopHost.System.GetConfigSection", mock_get_config):
            with pytest.raises(ValueError, match="ConfigFile configuration item not found"):
                ConfigLoader.load()
    
    def test_load_nonexistent_file(self, mock_hilltop_host):
        """Test error when config file doesn't exist."""
        mock_get_config = Mock(return_value={"ConfigFile": "C:\\nonexistent\\file.yaml"})
        
        with patch("HilltopHost.System.GetConfigSection", mock_get_config):
            with pytest.raises(FileNotFoundError, match="configuration file not found"):
                ConfigLoader.load()
    
    def test_load_empty_yaml_file(self, mock_hilltop_host, tmp_path):
        """Test loading an empty YAML file."""
        config_file = tmp_path / "empty_config.yaml"
        config_file.write_text("")
        
        mock_get_config = Mock(return_value={"ConfigFile": str(config_file)})
        
        with patch("HilltopHost.System.GetConfigSection", mock_get_config):
            config = ConfigLoader.load()
        
        assert config is None
    
    def test_load_yaml_with_nested_structure(self, mock_hilltop_host, tmp_path):
        """Test loading YAML with nested configuration structure."""
        config_file = tmp_path / "nested_config.yaml"
        config_content = """
OutsideRangeCheck:
  pH:
    critical:
      min: 5
      max: 9
    warning:
      min: 6
      max: 8
  disabled: false
"""
        config_file.write_text(config_content)
        
        mock_get_config = Mock(return_value={"ConfigFile": str(config_file)})
        
        with patch("HilltopHost.System.GetConfigSection", mock_get_config):
            config = ConfigLoader.load()
        
        assert "OutsideRangeCheck" in config
        assert "pH" in config["OutsideRangeCheck"]
        assert config["OutsideRangeCheck"]["pH"]["critical"]["min"] == 5
        assert config["OutsideRangeCheck"]["pH"]["critical"]["max"] == 9
        assert config["OutsideRangeCheck"]["disabled"] is False
    
    def test_load_yaml_with_lists(self, mock_hilltop_host, tmp_path):
        """Test loading YAML with list values."""
        config_file = tmp_path / "list_config.yaml"
        config_content = """
measurements:
  - pH
  - Temperature
  - Conductivity
"""
        config_file.write_text(config_content)
        
        mock_get_config = Mock(return_value={"ConfigFile": str(config_file)})
        
        with patch("HilltopHost.System.GetConfigSection", mock_get_config):
            config = ConfigLoader.load()
        
        assert "measurements" in config
        assert isinstance(config["measurements"], list)
        assert len(config["measurements"]) == 3
        assert "pH" in config["measurements"]
    
    def test_load_calls_get_config_section_correctly(self, mock_hilltop_host, tmp_path):
        """Test that GetConfigSection is called with correct parameter."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("key: value")
        
        mock_get_config = Mock(return_value={"ConfigFile": str(config_file)})
        
        with patch("HilltopHost.System.GetConfigSection", mock_get_config) as mock_func:
            ConfigLoader.load()
            mock_func.assert_called_once_with("sampler_qa_checks_demo")
