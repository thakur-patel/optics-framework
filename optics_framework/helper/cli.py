import argparse
import sys
from optics_framework.common.logging_config import apply_logger_format_to_all
from optics_framework.helper.list_keyword import main as list_main
from optics_framework.helper.config_manager import main as config_main
from optics_framework.helper.initialize import create_project
from optics_framework.helper.version import VERSION
from optics_framework.helper.execute import execute_main, dryrun_main
from optics_framework.helper.generate import generate_test_file as generate_framework_code

class Command:
    """
    Abstract base class for CLI commands.

    This abstract class defines the interface for CLI commands.
    Subclasses must implement the ``register`` and ``execute`` methods.

    :ivar logger: Optional logger instance.
    """

    def register(self, subparsers: argparse._SubParsersAction):
        """
        Register the command with the given subparsers.

        :param subparsers: The argparse subparsers object.
        :type subparsers: argparse._SubParsersAction
        :raises NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement the `register` method.")

    def execute(self, args: argparse.Namespace):
        """
        Execute the command using the provided arguments.

        :param args: The parsed command-line arguments.
        :type args: argparse.Namespace
        :raises NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement the `execute` method.")


@apply_logger_format_to_all("user")
class ListCommand(Command):
    """
    Command to list all available methods in the API.

    This command calls the :func:`list_main` function to display the available methods.
    """

    def register(self, subparsers: argparse._SubParsersAction):
        """
        Register the list command with the provided subparsers.

        :param subparsers: The argparse subparsers object.
        :type subparsers: argparse._SubParsersAction
        """
        parser = subparsers.add_parser(
            "list", help="List all available methods in the API"
        )
        parser.set_defaults(func=self.execute)

    def execute(self, args: argparse.Namespace):
        """
        Execute the list command.

        :param args: The parsed command-line arguments.
        :type args: argparse.Namespace
        """
        list_main()

@apply_logger_format_to_all("user")
class GenerateCommand(Command):
    """
    Command to generate test framework code.

    This command generates test framework code using the provided options.
    """

    def register(self, subparsers: argparse._SubParsersAction):
        """
        Register the generate command with the provided subparsers.

        :param subparsers: The argparse subparsers object.
        :type subparsers: argparse._SubParsersAction
        """
        parser = subparsers.add_parser("generate", help="Generate test framework code")
        parser.add_argument("project_path",
                            help="Project name (required)")
        parser.add_argument(
            "output_file",
            help="Path to the output file where the code will be generated",
            default="generated_test.py",
            nargs="?",
        )
        parser.set_defaults(func=self.execute)

    def execute(self, args: argparse.Namespace):
        """
        Execute the generate command.

        :param args: The parsed command-line arguments.
        :type args: argparse.Namespace
        """
        generate_framework_code(args.project_path, args.output_file)

class ConfigCommand(Command):
    """
    Command to manage configuration.

    This command delegates to the :func:`config_main` function for configuration management.
    """

    def register(self, subparsers: argparse._SubParsersAction):
        """
        Register the config command with the provided subparsers.

        :param subparsers: The argparse subparsers object.
        :type subparsers: argparse._SubParsersAction
        """
        parser = subparsers.add_parser("config", help="Manage configuration")
        parser.set_defaults(func=self.execute)

    def execute(self, args: argparse.Namespace):
        """
        Execute the config command.

        :param args: The parsed command-line arguments.
        :type args: argparse.Namespace
        """
        config_main()


@apply_logger_format_to_all("user")
class InitCommand(Command):
    """
    Command to initialize a new project.

    This command creates a new project using the provided options.
    """

    def register(self, subparsers: argparse._SubParsersAction):
        """
        Register the init command with the provided subparsers.

        :param subparsers: The argparse subparsers object.
        :type subparsers: argparse._SubParsersAction
        """
        parser = subparsers.add_parser("init", help="Initialize a new project")
        parser.add_argument("--name", required=True, help="Project name (required)")
        parser.add_argument(
            "--path", help="Directory where the project will be created"
        )
        parser.add_argument(
            "--force", action="store_true", help="Override if the project exists"
        )
        parser.add_argument(
            "--template", help="Select a project template (e.g., 'sample1')"
        )
        parser.add_argument(
            "--git-init",
            action="store_true",
            help="Initialize a git repository for the project",
        )
        parser.set_defaults(func=self.execute)

    def execute(self, args: argparse.Namespace):
        """
        Execute the init command.

        :param args: The parsed command-line arguments.
        :type args: argparse.Namespace
        """
        create_project(args)


@apply_logger_format_to_all("user")
class DryRunCommand(Command):
    """
    Command to generate a dry run report.

    This command generates a dry run report using CSV files for test cases, modules, and elements.
    """

    def register(self, subparsers: argparse._SubParsersAction):
        """
        Register the dry run command with the provided subparsers.

        :param subparsers: The argparse subparsers object.
        :type subparsers: argparse._SubParsersAction
        """
        parser = subparsers.add_parser(
            "dry_run", help="Execute test cases from CSV files"
        )
        parser.add_argument(
            "folder_path", type=str, help="Path to the folder containing CSV files"
        )
        parser.add_argument(
            "test_name",
            type=str,
            nargs="?",
            default="",
            help="Name of the test to execute. If not provided, all tests will run.",
        )
        parser.set_defaults(func=self.execute)

    def execute(self, args: argparse.Namespace):
        """
        Execute the dry run command.

        :param args: The parsed command-line arguments.
        :type args: argparse.Namespace
        """
        dryrun_main(args.folder_path, args.test_name)



@apply_logger_format_to_all("user")
class ExecuteCommand(Command):
    """
    Command to execute test cases from CSV files.

    This command runs test cases located in a specified folder, optionally filtering by test name.
    """

    def register(self, subparsers: argparse._SubParsersAction):
        """
        Register the execute command with the provided subparsers.

        :param subparsers: The argparse subparsers object.
        :type subparsers: argparse._SubParsersAction
        """
        parser = subparsers.add_parser(
            "execute", help="Execute test cases from CSV files"
        )
        parser.add_argument(
            "folder_path", type=str, help="Path to the folder containing CSV files"
        )
        parser.add_argument(
            "test_name",
            type=str,
            nargs="?",
            default="",
            help="Name of the test to execute. If not provided, all tests will run.",
        )
        parser.set_defaults(func=self.execute)

    def execute(self, args: argparse.Namespace):
        """
        Execute the test cases.

        :param args: The parsed command-line arguments.
        :type args: argparse.Namespace
        """
        execute_main(args.folder_path, args.test_name)


@apply_logger_format_to_all("user")
class VersionCommand(Command):
    """
    Command to display the current version of the Optics Framework.
    """

    def register(self, subparsers: argparse._SubParsersAction):
        """
        Register the version command with the provided subparsers.

        :param subparsers: The argparse subparsers object.
        :type subparsers: argparse._SubParsersAction
        """
        parser = subparsers.add_parser("version", help="Print the current version")
        parser.set_defaults(func=self.execute)

    def execute(self, args: argparse.Namespace):
        """
        Execute the version command.

        :param args: The parsed command-line arguments.
        :type args: argparse.Namespace
        """
        print(f"Optics Framework {VERSION}")


def main():
    """
    Main entry point for the Optics Framework CLI.

    This function sets up the argument parser, registers all commands, parses the
    command-line arguments, and dispatches the appropriate command function.
    """
    parser = argparse.ArgumentParser(prog="optics", description="Optics Framework CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Register all commands.
    commands = [
        ListCommand(),
        ConfigCommand(),
        DryRunCommand(),
        InitCommand(),
        ExecuteCommand(),
        VersionCommand(),
        GenerateCommand(),
    ]
    for cmd in commands:
        cmd.register(subparsers)

    args = parser.parse_args()

    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
