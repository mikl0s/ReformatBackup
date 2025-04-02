# Development Guide for ReformatBackup

This guide explains how to set up a development environment for ReformatBackup and outlines the development workflow.

## Setting Up the Development Environment

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/example/reformatbackup.git
   cd reformatbackup
   ```

2. Install the package in development mode with development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

   Alternatively, you can install from requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

3. Verify the installation:
   ```bash
   python -m reformatbackup.src.main --help
   ```

## Development Workflow

### Running the Application

To run the application in development mode:

```bash
python -m reformatbackup.src.main --debug
```

### Code Formatting and Linting

We use several tools to maintain code quality:

- **Black**: For code formatting
  ```bash
  black reformatbackup
  ```

- **isort**: For import sorting
  ```bash
  isort reformatbackup
  ```

- **flake8**: For linting
  ```bash
  flake8 reformatbackup
  ```

You can run all formatting and linting checks with:

```bash
black reformatbackup && isort reformatbackup && flake8 reformatbackup
```

### Running Tests

We use pytest for testing. To run the tests:

```bash
pytest
```

To run tests with coverage report:

```bash
pytest --cov=reformatbackup
```

To generate an HTML coverage report:

```bash
pytest --cov=reformatbackup --cov-report=html
```

The HTML report will be available in the `htmlcov` directory.

### Building the Package

To build the package for distribution:

```bash
python -m build
```

This will create distribution packages in the `dist` directory.

### Publishing to PyPI

To publish the package to PyPI:

```bash
twine upload dist/*
```

## Project Structure

```
reformatbackup/
├── src/                    # Core Python modules
│   ├── __init__.py         # Package initialization and version info
│   ├── main.py             # Entry point, Flask setup, browser launch
│   ├── scan.py             # App scanning logic (registry, file system)
│   ├── backup.py           # Backup functionality and metadata handling
│   ├── restore.py          # Restore functionality and version management
│   ├── utils.py            # Helper functions (7zip, JSON, etc.)
│   └── routes.py           # Flask routes and request handling
├── templates/              # HTML templates
├── static/                 # Static assets (CSS, JS, images)
├── tests/                  # Unit tests
├── pyproject.toml          # Package configuration
├── setup.cfg               # Configuration for development tools
├── pytest.ini              # Pytest configuration
├── requirements.txt        # Development dependencies
└── DEVELOPMENT.md          # This file
```

## Best Practices

1. **File Size Limit**: Keep each file under 500 lines of code. If a file exceeds this limit, refactor it by splitting into logical modules.

2. **Modularity**: Maintain the separation of concerns between modules. Each module should have a single responsibility.

3. **Testing**: Add or update tests in the `tests/` directory for any new functionality.

4. **Documentation**: Update docstrings and comments for any modified code.

5. **Type Hints**: Use Python type hints for better code readability and IDE support.

6. **Error Handling**: Use try/except blocks and log errors appropriately.

7. **Commit Messages**: Write clear, descriptive commit messages.

## Troubleshooting

### Common Issues

1. **Flask Server Not Starting**: Check for port conflicts or missing dependencies.
2. **Scanning Issues**: Verify Windows Registry access permissions.
3. **Backup/Restore Errors**: Check file permissions and disk space.
4. **UI Problems**: Inspect browser console for JavaScript errors.

### Debugging

1. Run with the `--debug` flag for detailed logging:
   ```bash
   python -m reformatbackup.src.main --debug
   ```

2. Check the log file in the user's home directory.
3. Use browser developer tools for UI issues.