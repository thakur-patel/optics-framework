import os
import asyncio
from typing import Optional, Tuple
from dataclasses import asdict
from optics_framework.common.logging_config import logger, apply_logger_format_to_all
from optics_framework.common.config_handler import ConfigHandler  # Updated import
from optics_framework.common.runner.csv_reader import CSVDataReader
from optics_framework.common.session_manager import SessionManager
from optics_framework.common.execution import ExecutionEngine


@apply_logger_format_to_all("user")
def find_csv_files(folder_path: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Search for CSV files in a folder and categorize them by reading their headers.

    :param folder_path: Path to the project folder.
    :return: Tuple of paths to test_cases, modules, and elements CSV files.
    """
    test_cases, modules, elements = None, None, None
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            file_path = os.path.join(folder_path, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    header = f.readline().strip().split(',')
                    headers = {h.strip().lower() for h in header}
            except (OSError, IOError) as e:
                logger.exception(f"Error reading {file_path}: {e}")
                continue

            if "test_case" in headers and "test_step" in headers:
                test_cases = file_path
                logger.debug(f"Found test cases file: {file_path}")
            elif "module_name" in headers and "module_step" in headers:
                modules = file_path
                logger.debug(f"Found modules file: {file_path}")
            elif "element_name" in headers and "element_id" in headers:
                elements = file_path
                logger.debug(f"Found elements file: {file_path}")
    return test_cases, modules, elements


@apply_logger_format_to_all("user")
class BaseRunner:
    """Base class for running test cases from CSV files using ExecutionEngine."""

    def __init__(self, folder_path: str, test_name: str = ""):
        self.folder_path = os.path.abspath(folder_path)
        self.test_name = test_name.strip()

        # Validate folder and CSV files
        if not os.path.isdir(self.folder_path):
            logger.error(f"Project folder does not exist: {self.folder_path}")
            raise ValueError(f"Invalid project folder: {self.folder_path}")
        test_cases_file, modules_file, elements_file = find_csv_files(
            self.folder_path)
        if not all([test_cases_file, modules_file, elements_file]):
            missing = [f for f, p in [
                ("test_cases", test_cases_file),
                ("modules", modules_file),
                ("elements", elements_file)
            ] if not p]
            logger.error(
                f"Missing required CSV files in {self.folder_path}: {', '.join(missing)}")
            raise ValueError(
                f"Incomplete CSV file set: missing {', '.join(missing)}")

        # Load CSV data
        csv_reader = CSVDataReader()
        self.test_cases_data = csv_reader.read_test_cases(test_cases_file)
        self.modules_data = csv_reader.read_modules(modules_file)
        self.elements_data = csv_reader.read_elements(elements_file)
        if not self.test_cases_data:
            logger.debug(f"No test cases found in {test_cases_file}")

        # Load and validate configuration using the new ConfigHandler
        self.config_handler = ConfigHandler.get_instance()
        self.config_handler.set_project(self.folder_path)
        self.config_handler.load()
        self.config = self.config_handler.config  # Now a Config dataclass instance

        # Ensure project_path is set in the Config object
        self.config.project_path = self.folder_path
        logger.debug(f"Loaded configuration: {self.config}")

        # Check required configs using the new get() method
        required_configs = [
            "driver_sources", "elements_sources"]
        missing_configs = [
            key for key in required_configs if not self.config_handler.get(key)]
        if missing_configs:
            logger.error(
                f"Missing required configuration keys: {', '.join(missing_configs)}")
            raise ValueError(
                f"Configuration missing required keys: {', '.join(missing_configs)}")

        # Setup session
        self.manager = SessionManager()
        # Pass the Config object as a dict for session creation
        self.session_id = self.manager.create_session(asdict(self.config))
        self.engine = ExecutionEngine(self.manager)

    async def run(self, mode: str):
        """Run the specified mode using ExecutionEngine."""
        try:
            await self.engine.execute(
                session_id=self.session_id,
                mode=mode,
                test_case=self.test_name if self.test_name else None,
                event_queue=None,  # Local mode uses TreeResultPrinter
                test_cases=self.test_cases_data,
                modules=self.modules_data,
                elements=self.elements_data
            )
        except Exception as e:
            logger.error(f"{mode.capitalize()} failed: {e}")
            raise
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up session resources."""
        try:
            self.manager.terminate_session(self.session_id)
        except Exception as e:
            logger.error(f"Failed to terminate session {self.session_id}: {e}")


@apply_logger_format_to_all("user")
class ExecuteRunner(BaseRunner):
    async def execute(self):
        """Execute test cases."""
        await self.run("batch")


@apply_logger_format_to_all("user")
class DryRunRunner(BaseRunner):
    async def execute(self):
        """Perform dry run of test cases."""
        await self.run("dry_run")


def execute_main(folder_path: str, test_name: str = ""):
    """Entry point for execute command."""
    runner = ExecuteRunner(folder_path, test_name)
    asyncio.run(runner.execute())


def dryrun_main(folder_path: str, test_name: str = ""):
    """Entry point for dry run command."""
    runner = DryRunRunner(folder_path, test_name)
    asyncio.run(runner.execute())


if __name__ == "__main__":
    folder_path = "/Users/dhruvmenon/Documents/optics-framework/Optics_Framework/optics_framework/samples/youtube/"
    execute_main(folder_path, "")
