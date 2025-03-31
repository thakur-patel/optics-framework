import json
import logging.config
from rich.logging import RichHandler
from contextlib import contextmanager
import threading
from pathlib import Path
from functools import wraps
from optics_framework.common.config_handler import ConfigHandler
from pythonjsonlogger.json import JsonFormatter

# --- Thread-local variable for temporary configuration ---
_log_context = threading.local()
_log_context.format_type = "internal"  # default mode is "internal"

# Get the singleton config instance
config_handler = ConfigHandler.get_instance()
config = config_handler.config
logger = logging.getLogger("optics_framework")

# --- Dynamic Filter ---

class DynamicFilter(logging.Filter):
    def filter(self, record):
        current = getattr(_log_context, "format_type", "internal")
        config_level_name = str(
            config_handler.get("log_level", "INFO")).upper()
        config_level = getattr(logging, config_level_name, logging.INFO)
        # Apply level filtering only in "user" mode for console; "internal" mode sees all
        if current == "user":
            return record.levelno >= config_level
        return True  # "internal" mode passes all logs to handlers

# --- Universal Formatter ---


class UniversalFormatter(logging.Formatter):
    def __init__(self):
        internal_fmt = (
            "[%(asctime)s] [%(levelname)-8s] %(message)-65s | "
            "%(name)s:%(funcName)s:%(lineno)d"
        )
        user_fmt = "%(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        self.datefmt = datefmt
        self.internal_formatter = logging.Formatter(
            internal_fmt, datefmt=datefmt)
        self.user_formatter = logging.Formatter(user_fmt)

    def format(self, record):
        fmt = getattr(_log_context, "format_type", "internal")
        for attr in ["test_case", "test_module", "keyword"]:
            if not hasattr(record, attr):
                setattr(record, attr, "N/A")
        if fmt == "user":
            return self.user_formatter.format(record)
        else:
            return self.internal_formatter.format(record)

    def __getattr__(self, name):
        if name == "_style":
            fmt = getattr(_log_context, "format_type", "internal")
            if fmt == "user":
                return self.user_formatter._style
            else:
                return self.internal_formatter._style
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'")


class EnhancedJsonFormatter(JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = self.formatTime(record)
        log_record["level"] = record.levelname
        log_record["message"] = record.msg
        log_record["test_case"] = getattr(record, "test_case", "N/A")
        log_record["test_module"] = getattr(record, "test_module", "N/A")
        log_record["keyword"] = getattr(record, "keyword", "N/A")
        log_record["logger"] = record.name
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)


class HierarchicalJsonHandler(logging.Handler):
    """
    Custom logging handler that accumulates log records into a nested dictionary.
    """

    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.logs = {}
        self.setFormatter(EnhancedJsonFormatter())

    def emit(self, record):
        try:
            json_record = self.format(record)
            log_entry = json.loads(json_record)
            test_case = log_entry.get("test_case", "N/A")
            test_module = log_entry.get("test_module", "N/A")
            keyword = log_entry.get("keyword", "N/A")
            self.logs.setdefault(test_case, {})
            self.logs[test_case].setdefault(test_module, {})
            self.logs[test_case][test_module].setdefault(
                keyword, []).append(log_entry)
        except Exception as e:
            self.handleError(record)

    def flush(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, indent=2)


logging.root.handlers = []

logger.setLevel(logging.DEBUG)  # Root logger captures all levels

# --- Console (Rich) Handler ---
console_level_name = str(config_handler.get("log_level", "INFO")).upper()
console_level = getattr(logging, console_level_name, logging.INFO)
rich_handler = RichHandler(
    rich_tracebacks=bool(config_handler.get("backtrace", True)),
    tracebacks_show_locals=bool(config_handler.get("diagnose", True)),
    show_time=True,
    show_level=True,
)
rich_handler.setFormatter(UniversalFormatter())
rich_handler.addFilter(DynamicFilter())
rich_handler.setLevel(console_level)  # Respect configured log level
logger.addHandler(rich_handler)

def initialize_additional_handlers():
    project_path = config_handler.get_project_path()
    if not project_path:
        logger.warning("Project path not set; defaulting to ~/.optics")
        project_path = str(Path.home() / ".optics")
    else:
        logger.debug(f"Using project path: {project_path}")

    # --- File Handler ---
    if config_handler.get("file_log", True):
        default_log_path = Path(project_path) / "execution_output" / "logs.log"
        configured_log_path = config_handler.config.get("log_path")
        log_path = Path(str(
            configured_log_path if configured_log_path is not None else default_log_path)).expanduser()
        logger.debug(f"Log file path: {log_path}")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, mode='w')
        file_handler.setFormatter(UniversalFormatter())
        file_handler.addFilter(DynamicFilter())
        file_handler.setLevel(logging.DEBUG)  # File captures all logs
        logger.addHandler(file_handler)

    # --- JSON Handler ---
    if config_handler.get("json_log", True):
        default_json_path = Path(project_path) / \
            "execution_output" / "logs.json"
        configured_json_path = config_handler.config.get("json_path")
        json_path = Path(str(
            configured_json_path if configured_json_path is not None else default_json_path)).expanduser()
        logger.debug(f"JSON log file path: {json_path}")
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_handler = HierarchicalJsonHandler(json_path)
        json_handler.setLevel(logging.DEBUG)  # JSON captures all logs
        logger.addHandler(json_handler)

# --- Context Manager and Decorators ---


@contextmanager
def set_logger_format(fmt: str):
    """
    Temporarily set the logger mode for the duration of a context.
    :param fmt: Logger mode ("internal" or "user").
    """
    old_format = getattr(_log_context, "format_type", "internal")
    _log_context.format_type = fmt
    try:
        yield
    finally:
        _log_context.format_type = old_format


def use_logger_format(fmt: str | None = None):
    """
    Decorator to automatically set the logger mode for a function call.
    :param fmt: Logger mode ("internal" or "user").
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with set_logger_format(fmt or "internal"):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def apply_logger_format_to_all(fmt: str | None = None):
    """
    Class decorator that applies a specific logger mode to every callable method.
    :param fmt: Logger mode for all methods in the class.
    """
    def decorator(cls):
        for attr_name in dir(cls):
            if not attr_name.startswith("__"):
                attribute = getattr(cls, attr_name)
                if callable(attribute):
                    decorated = use_logger_format(fmt)(attribute)
                    setattr(cls, attr_name, decorated)
        return cls
    return decorator
