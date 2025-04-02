### Coding Guidelines for the AI Coder

#### Project Overview
This guideline applies to the development of a Python-based Flask application for managing app backups and restores on Windows 11, distributed via PyPI. The tech stack includes Python 3.8+, Flask, `py7zr` for 7zip compression, and libraries like `winreg`, `psutil`, or `wmi` for system scanning. The app features a modern UI with light/dark themes, auto-updates, and JSON metadata handling.

#### General Principles
1. **File Size Limit:**  
   - Keep each file under 500 lines of code (excluding comments and blank lines).  
   - If a file exceeds 500 lines, refactor it by splitting into logical modules or functions in separate files (e.g., split `app.py` into `backup.py`, `restore.py`, `ui.py`).

2. **Modularity:**  
   - Organize code into small, reusable modules with single responsibilities (e.g., one module for scanning apps, another for backup logic).  
   - Use Python packages (e.g., `src/your_app/`) to group related files.

3. **Readability:**  
   - Follow PEP 8 for style (e.g., 4-space indents, 79-character line limit).  
   - Use descriptive variable/function names (e.g., `scan_installed_apps` instead of `scan`).  
   - Add docstrings to all modules, classes, and functions explaining purpose and parameters.

4. **Error Handling:**  
   - Catch and handle exceptions gracefully (e.g., file access errors, missing dependencies).  
   - Log errors to a file (e.g., `app.log`) using the `logging` module instead of `print`.

#### Tech Stack Specifics
1. **Python:**  
   - Use type hints where practical (e.g., `def backup_app(app_name: str) -> bool:`).  
   - Leverage standard libraries (e.g., `os`, `pathlib`) for file operations.  
   - Avoid external dependencies beyond Flask, `py7zr`, and minimal system utilities.

2. **Flask:**  
   - Define routes in a dedicated `routes.py` file if `app.py` grows large.  
   - Use Blueprints for modularizing routes (e.g., `backup_bp`, `restore_bp`).  
   - Keep templates in `templates/` and static files (CSS/JS) in `static/`, with subfolders for organization (e.g., `static/css/themes/`).

3. **py7zr:**  
   - Encapsulate 7zip operations in a utility module (e.g., `backup_utils.py`) to isolate compression logic.  
   - Ensure maximum compression is set explicitly (e.g., `with py7zr.SevenZipFile(..., mode='w', filters=[{'id': py7zr.FILTER_LZMA2, 'preset': 9}])`).

4. **UI (HTML/CSS/JS):**  
   - Use Bootstrap or Tailwind CSS for a modern, responsive design.  
   - Implement light/dark themes with CSS variables (e.g., `--bg-color`) and a JavaScript toggle, defaulting to dark.  
   - Keep JS files small and focused (e.g., `theme.js`, `backup.js`), under 500 lines each.

#### Project-Specific Rules
1. **File Structure:**  
   - Example layout:  
     your_app/  
     ├── src/  
     │   ├── __init__.py  
     │   ├── main.py         # Entry point, <500 lines  
     │   ├── scan.py        # App scanning logic  
     │   ├── backup.py      # Backup functionality  
     │   ├── restore.py     # Restore functionality  
     │   ├── utils.py       # Helpers (e.g., JSON, 7zip)  
     │   └── routes.py      # Flask routes  
     ├── templates/  
     │   ├── base.html      # Base template with theme toggle  
     │   └── apps.html      # App list and restore UI  
     ├── static/  
     │   ├── css/  
     │   │   └── styles.css # Theme definitions  
     │   └── js/  
     │       └── app.js     # UI interactions  
     ├── pyproject.toml     # Package config  
     └── README.md  
   - Split files if any exceed 500 lines (e.g., move large route handlers to `routes_backup.py`).

2. **Backup & Restore:**  
   - Store `.reformatbackup` and `appscan.json` in the user’s home directory with clear parsing logic in `utils.py`.  
   - Name backups as `<appname>-<timestamp>.7z` and JSON as `<appname>-<timestamp>.json`, handled in `backup.py`.  
   - Implement restore options (overwrite or backup-then-restore) as separate functions in `restore.py`.

3. **Auto-Updating:**  
   - Check PyPI versions in a small `update.py` module, triggered in `main.py`.  
   - Use `subprocess` to run `pip install --upgrade` if approved by the user.

4. **UI Features:**  
   - Add a theme toggle in `base.html` and `app.js`, defaulting to dark mode via CSS.  
   - Display app list and restore versions in `apps.html` with dynamic Jinja2 templating.  
   - Keep UI logic modular (e.g., separate JS for theme switching vs. backup triggers).

#### Best Practices
1. **Version Control:**  
   - Use Git with meaningful commit messages (e.g., “Add dark theme toggle to UI”).  
   - Tag releases for PyPI (e.g., `v1.0.0`).

2. **Testing:**  
   - Write unit tests in a `tests/` folder using `pytest` (e.g., `test_backup.py`).  
   - Mock system calls (e.g., `winreg`) to avoid real file changes during tests.

3. **Documentation:**  
   - Include inline comments for complex logic (e.g., app scanning).  
   - Update README with setup, usage, and theme instructions.

#### Enforcement
- Use a linter (e.g., `flake8`) to enforce PEP 8 and check line counts.  
- Refactor any file exceeding 500 lines before finalizing a feature (e.g., split `main.py` into `main.py` and `core.py`).

