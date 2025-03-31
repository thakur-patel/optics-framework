Developer Guide
===============

This section provides guidelines for developers who want to contribute to the Optics Framework.

Note: Before contributing, please read our `Contributing Guidelines <contributing_guidelines>` to understand the contribution process. 

1. Setting Up the Development Environment
-----------------------------------------

To set up the development environment for the Optics Framework, follow these steps:

**Clone the Repository:** Clone the Optics Framework repository to your local machine using the following command:

.. code-block:: bash

    git clone <repository_url>
    cd optics-framework

**Install Dependencies:** Install the required dependencies using the following command:

.. code-block:: bash

    pipx install poetry

For Changes related to source code:

.. code-block:: bash

    poetry install --with dev

For Changes related to documentation:

.. code-block:: bash

    poetry install --with docs

For default installation:

.. code-block:: bash

    poetry install

**NOTE:** We recommend using `poetry` to manage dependencies and virtual environments for the project.
**NOTE:** For more info about pipx and poetry, refer to the `pipx documentation <https://pipxproject.github.io/pipx/>`_ and `poetry documentation <https://python-poetry.org/docs/>`_.

2. Create a New Branch
-----------------------

Before making any changes to the codebase, create a new branch for your contribution using the following command:

.. code-block:: bash

    git checkout -b <branch_name>

3. Make Changes

Work on your feature, bug fix, or documentation improvement in the appropriate directory:
- Source code: optics_framework/
- Tests: tests/
- Documentation: docs/

**Source Code Changes:**
- Make changes to the source code in the optics_framework/ directory.

Adhere to the project’s coding standards:
    Use Black for linting and formatting:

    .. code-block:: bash

        poetry run black .

**Documentation Changes:**

- Make changes to the documentation in the docs/ directory.
- Ensure the documentation is clear, concise, and follows the style guide.
- Use Sphinx for generating documentation.

For Live Changes while working on documentation:

- Use Sphinx to automatically rebuild your documentation as you make changes:

.. code-block:: bash

    poetry run sphinx-autobuild docs/source docs/build/html

**Run Tests:**
- Run the tests to ensure that your changes do not break existing functionality:

.. code-block:: bash

    poetry run pytest

**Packaging:**
- To build the package:

.. code-block:: bash

    poetry build


3. Commit Changes

- Adhere to the `Conventional Commits <https://www.conventionalcommits.org/en/v1.0.0/>`_ format for your commit messages.

