Prompt for AI Coder:

I need you to develop a Python-based application using Flask that is installable and runnable with a single command (e.g., `pip install reformatbackup && reformatbackup`), with the following specifications. The solution should be a Python package distributed via PyPI, requiring no manual compilation—just standard Python script execution.

1. Distribution and Setup:
   - Package the application as a Python module uploadable to PyPI, installable with `pip install reformatbackup`.
   - Define a command-line entry point (e.g., `reformatbackup`) in `setup.py` or `pyproject.toml` for immediate execution post-install.
   - Include all dependencies (e.g., Flask, py7zr for 7zip) in the package configuration, installed automatically via pip.

2. Auto-Updating:
   - Implement an auto-update feature that checks PyPI for newer versions on startup (e.g., using `pip index versions reformatbackup` or a version API).
   - Prompt the user in the UI to update with a single command (e.g., `pip install --upgrade reformatbackup`), ideally automating the process with a button click.

3. Core Functionality:
   - When run (e.g., `reformatbackup`), launch a Flask web server that opens a dynamic web interface in the user’s default browser.
   - Display a list of all installed applications on Windows 11, including:
     - Name of each application.
     - Approximate size (in MB or GB).
     - Drive where installed (e.g., C:, D:).
     - Total sizes per drive and a grand total across all drives.
     - Last backup date for each app (if a backup exists, extracted from the filename).

4. Backup Functionality:
   - Allow users to set a backup location (e.g., `D:\Backups\`) via the UI, stored in a `.reformatbackup` file in the user’s home folder (e.g., `C:\Users\<Username>\`) by default, with a custom location option.
   - Enable selection of one or more apps to back up.
   - For each selected app:
     - Back up associated user folders (e.g., `AppData\Local\<AppName>`, `AppData\Roaming\<AppName>`, `Documents` if applicable).
     - Compress into a 7zip file with maximum compression using `py7zr`, named `<appname>-<timestamp>.7z` (e.g., `notepad-20250402-190431.7z`, timestamp in `YYYYMMDD-HHMMSS`).
     - Save backups to the user-defined location.

5. Restore Functionality:
   - Add a "Restore" section in the UI showing all backup versions for each app (e.g., a dropdown or list of timestamps).
   - Provide two restore options:
     - Restore over existing settings by extracting the selected backup to the app’s user folders.
     - Back up the current state first, then load the selected backup version.
   - Display metadata (e.g., size, date) for each backup version in the UI.

6. Backup Notes & Metadata:
   - For each backup, create a JSON file with the same name (e.g., `notepad-20250402-190431.json`) containing:
     - User-added notes (editable via the UI).
     - Metadata: timestamp, backup size, app name, source paths.
   - Store JSON files alongside the .7z backups in the backup location.

7. UI Design:
   - Design a great, modern-looking UI for app management and restores using Flask templates (HTML/CSS/JavaScript).
   - Ensure a clean, responsive layout (e.g., using Bootstrap or Tailwind CSS) with:
     - App list with checkboxes, sizes, drives, and backup dates.
     - Backup location input and “Backup Selected” button.
     - Restore section with version selection and action buttons.
     - Notes input field per backup.
     - Progress feedback (e.g., “Backing up…” or “Restoring…”).
     - Light/dark themes with dark as the default, including a toggle to switch between them (e.g., via CSS classes and JavaScript).

8. Development Features:
   - Dynamic Web Interface: Serve UI from Flask templates (`templates`/`static` folders), supporting local filesystem loading during development, bundled in the final package.
   - Cached Scan Data: Save app scan results to `appscan.json` in the home folder or configurable location, loadable without rescanning, with a `--rescan` flag or UI toggle.

9. Technical Requirements:
   - Ensure compatibility with Windows 11 and Python 3.8+.
   - Use `psutil`, `winreg`, or `wmi` for app scanning, Flask for the web server, and `py7zr` for 7zip compression—all as pip dependencies.
   - Handle edge cases (e.g., missing backup location, permissions) within Python.

10. Deliverables:
    - A PyPI package installable via `pip install reformatbackup`.
    - Source code with comments on key components (e.g., scanning, backup/restore, Flask setup).
    - A README with:
      - Install/run instructions (e.g., `pip install reformatbackup && reformatbackup`).
      - Update instructions (e.g., `pip install --upgrade reformatbackup`).
      - Cached scan and UI development details.

11. Key Emphasis:
    - Installable/runnable with one command, assuming Python is present.
    - Auto-updates for seamless maintenance.
    - Modern, user-friendly UI with light/dark themes (dark default) and robust backup/restore features.
    - No compilation—just Python and pip.

Please ensure the solution is polished, efficient, and delivers a great user experience with a sleek, themeable UI. Let me know if you need clarification!


