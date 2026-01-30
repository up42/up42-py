# UP42 SDK Developer Readme

## Installation

1. **Clone the repository:**

```bash
git clone git@github.com:up42/up42-py.git
cd up42-py
```

2. **Install development environment**

   1. Install [asdf](https://asdf-vm.com/)
   2. Install python support via `asdf plugin-add python`
   3. Install poetry support via `asdf plugin-add poetry`
   4. Install environment via `asdf install`

3. **Install dependencies using Poetry:**

[Poetry](https://python-poetry.org/) is a dependency management and packaging tool for Python.

You can install the project dependencies:

```bash
poetry install
```

This will create a virtual environment and install the dependencies specified in `pyproject.toml`.

4. **IDE Setup**

It's recommended to use Pycharm IDE, it fully supports Poetry managed environments.

## Development Setup

1. **Install pre-commit hooks:**

This project uses [pre-commit](https://pre-commit.com/) hooks to enforce code quality checks before commits. To install and set up pre-commit hooks, run the following:

```bash
poetry run pre-commit install
```

This will install the hooks defined in `.pre-commit-config.yaml` and ensure that they run automatically before each commit.

2. **Optional: Run pre-commit hooks manually:**

You can run the pre-commit hooks manually at any time with the following command:

```bash
poetry run pre-commit run --all-files
```

## Pre-commit Hooks

This repository uses the following main pre-commit hooks to ensure code quality:

- **black**: Automatically formats Python code to comply with PEP 8.
- **isort**: Sorts import statements alphabetically and automatically separates them into sections.
- **flake8**: Checks for style violations and errors in the code.
- **mypy**: Performs static type checking of the code.
- **pylint**: Analyzes Python code for potential errors, coding standards violations, and refactor suggestions.

## Testing

This project uses `pytest` for testing. Follow the instructions below to set up and run tests.

### 1. Install Testing Dependencies

`pytest` is included as a development dependency in this project. If you haven't done so yet, you can install the testing dependencies by running:

```bash
poetry install
```

### 2. Running Tests

You can run the tests with `pytest` using the following command:

```bash
poetry run pytest
```

This will discover and run all the tests in the `tests/` folder.

### 3. Running Tests in Pycharm

To run tests directly from the PyCharm interface:

1. Right-click the test file or folder (e.g., tests/).
2. Select Run 'pytest in tests'.

PyCharm will use the Poetry environment for running the tests and display the results in the run console.

## Environment Variables
| VARIABLE NAME               | DESCRIPTION                                                                                                                                                        |
|-----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| UP42_DISABLE_VERSION_CHECK  | Used by the SDK to determine if it should check if the latest version of the SDK is being used or not. This is a `boolean` variable so please either set it to `True` or `False` |
