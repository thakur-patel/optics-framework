from pathlib import Path
import json
import pytest
from optics_framework.common.logging_config import LoggerConfig, LoggerSetup


@pytest.fixture
def default_config():
    return {
        "log_level": "DEBUG",
        "console": True,
    }


def test_default_config_loading(mocker, default_config):
    mocker.patch.object(LoggerConfig, "load_config",
                        return_value=default_config)
    config = LoggerConfig.load_config()
    assert isinstance(config, dict)
    assert config["log_level"] == "DEBUG"
    assert config["console"] is True


def test_logger_file_creation(tmp_path, mocker):
    config_path = tmp_path / "logger_config.json"
    config_data = {
        "log_level": "INFO",
        "console": False,
        "file_log": True,
        "log_path": str(tmp_path / "logs.log"),
    }
    config_path.write_text(json.dumps(config_data))
    mocker.patch.object(LoggerConfig, "CONFIG_FILE", Path(config_path))
    logger_setup = LoggerSetup(LoggerConfig())
    assert logger_setup.config["log_level"] == "INFO"
    assert not logger_setup.config["console"]
