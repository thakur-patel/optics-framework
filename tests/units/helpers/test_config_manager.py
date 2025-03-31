import pytest
import json
from pathlib import Path
from optics_framework.helper.config_manager import ConfigManager


def test_load_default_config(tmp_path):
    """Test that the default config is loaded when no config file exists."""
    config_file = tmp_path / "logger_config.json"
    ConfigManager.CONFIG_FILE = config_file  # Override for testing

    config = ConfigManager.load_config()
    assert config == ConfigManager.DEFAULT_CONFIG


def test_config_save_and_load(tmp_path):
    """Test saving and loading a valid configuration."""
    config_file = tmp_path / "logger_config.json"
    ConfigManager.CONFIG_FILE = config_file  # Override for testing

    test_config = {"log_level": "INFO", "console": False, "file_log": True}
    ConfigManager.save_config(test_config)

    loaded_config = ConfigManager.load_config()
    assert loaded_config == test_config


def test_config_directory_creation(tmp_path):
    """Test that the config directory is created when saving."""
    config_dir = tmp_path / "config"
    config_file = config_dir / "logger_config.json"
    ConfigManager.CONFIG_DIR = config_dir  # Override for testing
    ConfigManager.CONFIG_FILE = config_file

    test_config = {"log_level": "DEBUG"}
    ConfigManager.save_config(test_config)

    assert config_dir.exists()
    assert config_file.exists()


def test_load_corrupt_config(tmp_path):
    """Test loading a corrupt JSON file falls back to default configuration."""
    config_file = tmp_path / "logger_config.json"
    ConfigManager.CONFIG_FILE = config_file  # Override for testing

    with open(config_file, "w", encoding="utf-8") as f:
        f.write("{invalid_json}")

    config = ConfigManager.load_config()
    assert config == ConfigManager.DEFAULT_CONFIG


def test_load_invalid_permission(tmp_path):
    """Test handling of permission errors when loading the config."""
    config_file = tmp_path / "logger_config.json"
    ConfigManager.CONFIG_FILE = config_file  # Override for testing

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump({"log_level": "INFO"}, f)

    config_file.chmod(0o000)  # Remove all permissions

    try:
        config = ConfigManager.load_config()
        assert config == ConfigManager.DEFAULT_CONFIG
    finally:
        config_file.chmod(0o644)  # Restore permissions for cleanup
