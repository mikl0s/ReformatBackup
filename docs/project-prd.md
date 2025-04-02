# Product Requirements Document (PRD)

## Product Name
AppBackup Manager

## Version
1.0

## Date
April 02, 2025

## Overview

### Purpose
AppBackup Manager is a lightweight, user-friendly tool designed to simplify the backup and restoration of application-specific user settings and data on Windows 11. It targets tech-savvy users, IT professionals, and gamers who need a portable, efficient solution to preserve app configurations without full system backups.

### Goals
- Provide a single-command installable Python application via PyPI.
- Offer a modern, themeable web interface for managing app backups and restores.
- Enable seamless auto-updates and robust backup/restore functionality with metadata and notes.
- Ensure portability and ease of use with no manual compilation required.

### Target Audience
- Windows 11 users needing to migrate or safeguard app settings.
- Developers seeking a flexible, iterable tool for app data management.

## Features

### 1. Installation & Distribution
- Requirement: Installable and runnable with a single command (e.g., `pip install appbackup-manager && appbackup-manager`).
- Details: Distributed as a Python package on PyPI, with all dependencies (Flask, py7zr, etc.) auto-installed via pip.
- Success Criteria: Users can install and launch the app in one terminal command, assuming Python 3.8+ is present.

### 2. Auto-Updating
- Requirement: Automatically check for updates and prompt the user to upgrade.
- Details: On startup, query PyPI for newer versions and offer a one-click update via `pip install --upgrade appbackup-manager`.
- Success Criteria: Users see an update prompt in the UI when a new version is available and can update without manual intervention.

### 3. App Scanning & Display
- Requirement: List all installed Windows 11 applications with relevant details.
- Details: Display app name, size (MB/GB), drive location, total sizes per drive, and grand total across drives in a web UI. Show last backup date if applicable.
- Success Criteria: Accurate, up-to-date app list loads in under 10 seconds on a typical system.

### 4. Backup Functionality
- Requirement: Back up selected apps’ user data into 7zip files.
- Details: 
  - User sets a backup location (stored in `.reformatbackup` in home folder, customizable).
  - Select apps via checkboxes; back up user folders (e.g., AppData, Documents).
  - Create `<appname>-<timestamp>.7z` files (e.g., `notepad-20250402-190431.7z`) with maximum compression.
- Success Criteria: Backups complete without errors, files are compressed and named correctly.

### 5. Restore Functionality
- Requirement: Restore app settings from backups with version management.
- Details: 
  - Show all backup versions per app in a “Restore” UI section (e.g., dropdown/list).
  - Offer two options: overwrite existing settings or back up current state then restore selected version.
- Success Criteria: Restores accurately replace or update app settings; dual-option workflow is intuitive.

### 6. Backup Notes & Metadata
- Requirement: Store notes and metadata with each backup.
- Details: 
  - Create `<appname>-<timestamp>.json` files alongside .7z files.
  - Include user-editable notes and metadata (timestamp, size, app name, source paths).
- Success Criteria: JSON files are generated and editable via the UI, containing all required data.

### 7. User Interface
- Requirement: Provide a modern, themeable web UI.
- Details: 
  - Use Flask templates with Bootstrap/Tailwind CSS for a clean, responsive design.
  - Include app list, backup controls, restore section, notes input, and progress feedback.
  - Support light/dark themes (dark default) with a toggle.
- Success Criteria: UI is visually appealing, responsive on all screen sizes, and theme switch works instantly.

### 8. Development Features
- Requirement: Support rapid iteration during development.
- Details: 
  - Dynamic UI loading from local templates/static files during dev, bundled in the package.
  - Cache app scans in `appscan.json` (home folder, configurable), with a rescan option (flag/UI toggle).
- Success Criteria: Developers can iterate UI without rescanning; cached data loads correctly.

## Technical Requirements

### Platform
- Windows 11

### Tech Stack
- Language: Python 3.8+
- Web Framework: Flask
- Compression: py7zr (7zip)
- System Access: `winreg`, `psutil`, or `wmi` for app scanning
- Dependencies: Managed via pip, included in PyPI package

### Performance
- App scan completes in <10 seconds on a standard Windows 11 system.
- Backup/restore operations provide real-time UI feedback.
- Memory usage stays below 200 MB during typical operation.

### Constraints
- No manual compilation; pure Python execution.
- Files must not exceed 500 lines (refactor/split if larger).
- Python must be pre-installed by the user.

## Deliverables
1. PyPI Package: `appbackup-manager`, installable via `pip install appbackup-manager`.
2. Source Code: Well-commented, split into modules (e.g., `main.py`, `backup.py`, `restore.py`).
3. Documentation: README with install, run, update, and dev instructions.

## Non-Functional Requirements
- Usability: Intuitive UI with minimal learning curve.
- Reliability: Error-free backups/restores; robust exception handling.
- Maintainability: Modular code, <500 lines per file, clear comments.

## Assumptions
- Users have Python 3.8+ installed (available via Microsoft Store).
- Windows 11 permissions allow access to AppData and other user folders.

## Risks
- Risk: Limited app detection accuracy due to Windows API variability.  
  Mitigation: Use multiple scanning methods (e.g., Registry, WMI) and allow manual app addition.
- Risk: UI performance lag with many backups.  
  Mitigation: Paginate app/backup lists in the UI.

## Success Metrics
- 95% of backups/restores complete without errors.
- UI loads in <2 seconds; theme toggle is instantaneous.
- Positive user feedback on ease of use and design.