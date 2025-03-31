Usage Guide
===========

This section describes the available commands for the `optics-framework` CLI.

Executing Test Cases
--------------------

Run test cases with the following command:

.. code-block:: bash

   optics execute <project_path> --test-cases <test_case_name>

**Options:**

- `<project_path>` : Path to the project directory.
- `--test-cases <test_case_name>` : Path to the test cases file.

------------------------------------------------------------------------------------------------------------

Initializing a New Project
--------------------------

Use the following command to initialize a new project:

.. code-block:: bash

   optics init --name <project_name> --path <directory> \
                  --template <sample_name> --git-init

**Options:**

- `--name <project_name>` : Name of the project.
- `--path <directory>` : Directory to create the project in.
- `--force` : Overwrite existing files if necessary.
- `--template <sample_name>` : Choose a predefined example.
- `--git-init` : Initialize a Git repository.

------------------------------------------------------------------------------------------------------------

Generating Code
---------------

**TODO**

Generate test automation code from an input CSV file:

.. code-block:: bash

   optics generate <input_csv> --output <output_generated_code>

**Options:**
- `<input_csv>` : Path to the input CSV file.
- `--output <output_generated_code>` : Specify the output file.

------------------------------------------------------------------------------------------------------------

Listing Available Keywords
--------------------------

Display a list of all available keywords:

.. code-block:: bash

   optics list

------------------------------------------------------------------------------------------------------------

Executing Dry Run
--------------------------
Execute a dry run of all test cases:

.. code-block:: bash

   optics dry_run <project_path>

Execute a dry run of a specific test case:

.. code-block:: bash

   optics dry_run <project_path> --test-case "<test-case-name>"

**Options:**
- `<project_path>` : Path to the project directory.
- `--test-case "<test-case-name>"` : Specify the test case to execute.

------------------------------------------------------------------------------------------------------------

Showing Help Information
------------------------

Get help for the CLI:

.. code-block:: bash

   optics-framework --help

------------------------------------------------------------------------------------------------------------

Managing Configuration
----------------------

Set, reset, or list configuration values:

.. code-block:: bash

   optics-framework config --set <key> <value> --reset --list

**Options:**

- `--set <key> <value>` : Set a configuration key-value pair.
- `--reset` : Reset all configurations to default.
- `--list` : Display current configuration values.

------------------------------------------------------------------------------------------------------------

Checking Version
----------------

Check the installed version of `optics-framework`:

.. code-block:: bash

   optics-framework --version
