# ReformatBackup Codebase Summary

## Overview

ReformatBackup is a Python-based Flask application designed to simplify the backup and restoration of application-specific user settings and data on Windows 11. It provides a modern web interface for users to manage app backups and restores, with features like auto-updates, themeable UI, and robust backup/restore functionality with metadata and notes.

This document provides an overview of the codebase structure, architecture, and key components to help new developers understand how to make changes to the project.

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
│   ├── base.html           # Base template with theme toggle
│   ├── index.html          # Main app list view
│   ├── backup.html         # Backup interface
│   └── restore.html        # Restore interface
├── static/                 # Static assets
│   ├── css/
│   │   ├── styles.css      # Main styles
│   │   └── themes.css      # Theme definitions (light/dark)
│   ├── js/
│   │   ├── app.js          # Main UI logic
│   │   ├── backup.js       # Backup functionality
│   │   ├── restore.js      # Restore functionality
│   │   └── theme.js        # Theme switching
│   └── img/
│       └── logo.png        # App logo
├── tests/                  # Unit tests
│   ├── test_scan.py
│   ├── test_backup.py
│   ├── test_restore.py
│   └── test_utils.py
├── pyproject.toml          # Package configuration
├── requirements.txt        # Development dependencies
├── setup.cfg               # Configuration for development tools
├── pytest.ini              # Pytest configuration
├── DEVELOPMENT.md          # Development guide
└── __init__.py             # Root package initialization
```

## Key Components

### 1. Entry Point and Flask Setup (`main.py`)

The application entry point is in `main.py`, which:
- Initializes the Flask application using the application factory pattern
- Sets up configuration for development and production environments
- Registers error handlers for common HTTP errors
- Sets up command-line argument parsing
- Checks for updates on PyPI and provides update functionality
- Launches the default web browser
- Starts the Flask server with appropriate configuration

The main function is registered as a console script entry point in `pyproject.toml`, allowing the application to be run with the `reformatbackup` command after installation.

The application includes a one-click update mechanism that creates a temporary script to update the package using pip, which runs in a separate process to avoid interrupting the current session.

### 2. Application Scanning (`scan.py`)

The scanning module is responsible for:
- Detecting installed applications via Windows Registry (including Microsoft Store apps)
- Scanning the file system for applications across multiple drives
- Finding application-specific dot files and configuration directories
- Calculating application sizes with optimized performance
- Caching scan results in `appscan.json` with detailed metadata
- Providing sorting and filtering capabilities

The scanning process uses multiple detection methods:
1. **Registry Scanning**: Scans Windows Registry for installed applications, Microsoft Store apps, and Windows App Paths
2. **File System Scanning**: Scans common installation directories, game libraries (Steam, Epic, GOG), and all available drives
3. **Dot Files Scanning**: Identifies application-specific configuration files and directories in the user's home directory

The scanning process is resource-intensive, so results are cached to improve performance on subsequent runs. A `--rescan` flag or UI toggle can force a fresh scan. The UI provides sorting options (by name, size, or drive) and filtering capabilities to help users navigate large application lists.

### 3. Configuration Management (`config.py`)

The configuration module handles:
- Reading and writing application settings to `.reformatbackup` in the user's home directory
- Managing backup location, theme preferences, and update settings
- Providing default configuration values
- Validating user inputs for configuration settings
- Handling configuration errors gracefully

The configuration file is a JSON file with settings for backup location, auto-rescan, theme, update checking, and other application preferences.

### 4. Backup Functionality (`backup.py`)

The backup module handles:
- Identifying application data locations
- Compressing data using 7zip (via `py7zr`)
- Creating metadata JSON files with timestamps and notes
- Handling dot files and hidden directories
- Managing backup versions with automatic cleanup of old backups

Backups are named with the pattern `<appname>-<timestamp>.7z` and stored in the user-defined backup location.

### 5. Restore Functionality (`restore.py`)

The restore module manages:
- Listing available backup versions for an application
- Extracting backups to their original locations
- Optionally backing up current state before restoring
- Handling metadata and version management

Two restore options are provided: direct restore or backup-then-restore.

### 6. Utility Functions (`utils.py`)

Common utility functions include:
- 7zip compression and extraction
- JSON reading and writing
- Hidden file handling
- Size formatting
- Timestamp formatting

### 7. Flask Routes (`routes.py`)

The routes module defines all HTTP endpoints:
- Main application view (`/`)
- Backup endpoint (`/backup`)
- Restore view and action (`/restore/<app_id>` and `/restore/<app_id>/<backup_id>`)
- Settings management (`/settings`)
- Update management (`/update`)
- Configuration API endpoints (`/settings/update-check`)

The routes are set up using a function-based approach with proper error handling and type hints. Helper functions for calculating drive sizes and retrieving recent backups are also included.

### 8. User Interface

The UI is built with:
- Flask templates (Jinja2)
- Bootstrap for responsive layout
- Custom CSS for styling and themes
- JavaScript for interactivity, theme switching, and update management

The interface supports both light and dark themes, with dark as the default. Theme preferences are stored in both localStorage and the application configuration file. The application also supports system theme detection for automatic switching based on user preferences.

The main application view includes:
- A sortable and filterable list of detected applications
- Visual indicators for application sources (Registry, File System, Dot Files)
- Detailed application metadata (size, location, publisher, version)
- Statistics about scanned applications and drive usage
- A modal dialog explaining the scanning process and detection methods

The UI includes a settings page for managing backup location, theme preferences, update settings, and other application options. It also features an update notification system with a modal dialog for one-click updates.

Error handling is implemented with dedicated error templates that provide user-friendly error messages while logging detailed information for debugging.

## Configuration Files

### 1. User Configuration

- `.reformatbackup`: JSON file in the user's home directory storing all application settings:
  - Backup location
  - Theme preference
  - Update checking settings
  - Auto-rescan settings
  - Compression level
  - Maximum backups per application
- `appscan.json`: Cache of scanned applications to improve performance

### 2. Package Configuration

- `pyproject.toml`: Defines package metadata, dependencies, and entry points
- `requirements.txt`: Lists development dependencies
- `setup.cfg`: Configures development tools like flake8 and isort
- `pytest.ini`: Configures pytest for testing

## Development Workflow

### Setting Up Development Environment

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
   
   Alternatively, you can install from requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```
   
3. Run the application in development mode:
   ```bash
   python -m reformatbackup.src.main --debug
   ```

4. For detailed development instructions, refer to the DEVELOPMENT.md file in the project root.

### Making Changes

When making changes to the codebase, keep in mind:

1. **File Size Limit**: Keep each file under 500 lines of code. If a file exceeds this limit, refactor it by splitting into logical modules.

2. **Modularity**: Maintain the separation of concerns between modules. Each module should have a single responsibility.

3. **Testing**: Add or update tests in the `tests/` directory for any new functionality.

4. **Documentation**: Update docstrings and comments for any modified code.

5. **UI Changes**: 
   - HTML templates are in the `templates/` directory
   - CSS styles are in `static/css/`
   - JavaScript is in `static/js/`
   - Theme support is implemented in `themes.css` and `theme.js`

### Testing Changes

Run tests using pytest:
```bash
pytest
```

Run tests with coverage report:
```bash
pytest --cov=reformatbackup
```

Generate an HTML coverage report:
```bash
pytest --cov=reformatbackup --cov-report=html
```

### Building and Installing

Build the package:
```bash
python -m build
```

Install locally:
```bash
pip install .
```

## Key Concepts
### 1. Application Detection

Applications are detected through multiple methods:
- Windows Registry scanning (including Microsoft Store apps and Windows App Paths)
- File system scanning of common installation directories and all available drives
- Game library detection (Steam, Epic Games, GOG)
- Dot file detection in the user's home directory
- Application-specific configuration directories
- AppData folder scanning for user settings

The application uses intelligent detection to identify executables and application data, while filtering out system files and directories. Duplicate applications are handled by keeping the entry with the most complete information.
- Dot file detection in the user's home directory

### 2. Backup and Restore Process

The backup process:
1. Identify application data locations
2. Compress data using 7zip
3. Create metadata JSON file
4. Store in user-defined location

The restore process:
1. Extract backup to temporary location
2. Optionally back up current state
3. Copy files to original locations
4. Clean up temporary files

### 3. Configuration Management

User settings are stored in:
- `.reformatbackup` for backup location
- `appscan.json` for cached scan results

### 4. Theme Support

The application supports light and dark themes:
- Theme preference is stored in localStorage
- CSS variables define theme colors
- JavaScript handles theme switching

## Common Tasks

### Adding a New Feature

1. Identify which module(s) need to be modified
2. Make changes to the relevant Python files
3. Update or add templates if UI changes are needed
4. Add CSS/JS for any new UI components
5. Add tests for the new functionality
6. Update documentation if necessary

### Fixing a Bug

1. Identify the source of the bug
2. Add a test case that reproduces the bug
3. Fix the bug in the relevant module
4. Verify that the test now passes
5. Update documentation if necessary

### Adding a New Route

1. Add the route function in `routes.py`
2. Create any necessary templates in the `templates/` directory
3. Add CSS/JS for the new page if needed
4. Update navigation links if necessary

## Best Practices

1. **Error Handling**: Use try/except blocks and log errors appropriately
2. **Type Hints**: Use Python type hints for better code readability and IDE support
3. **Documentation**: Keep docstrings and comments up to date
4. **Testing**: Write tests for new functionality
5. **Code Style**: Follow PEP 8 guidelines (enforced by flake8)
6. **Code Formatting**: Use Black and isort for consistent code formatting
7. **Commit Messages**: Write clear, descriptive commit messages

## Troubleshooting

### Common Issues

1. **Flask Server Not Starting**: Check for port conflicts or missing dependencies
2. **Scanning Issues**: Verify Windows Registry access permissions
3. **Backup/Restore Errors**: Check file permissions and disk space
4. **UI Problems**: Inspect browser console for JavaScript errors

### Debugging

1. Run with the `--debug` flag for detailed logging
2. Check the log file in the user's home directory
3. Use browser developer tools for UI issues

## Future Development

Areas for potential enhancement:

1. **Performance Optimization**: Further improve scanning speed for large systems
2. **UI Enhancements**: Add more interactive features and visualizations
3. **Additional Backup Options**: Support for cloud storage or network locations
4. **Scheduled Backups**: Add ability to schedule automatic backups
5. **Multi-platform Support**: Extend beyond Windows 11
6. **Game Library Integration**: Deeper integration with game platforms for better backup/restore
7. **Application Grouping**: Allow users to organize applications into custom groups
8. **Backup Compression Options**: Provide different compression levels and formats

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [py7zr Documentation](https://py7zr.readthedocs.io/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [Windows Registry API](https://docs.python.org/3/library/winreg.html)