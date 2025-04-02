<div align="center">

# 🔄 AppBackup Manager

<img src="https://img.shields.io/badge/platform-Windows%2011-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Platform: Windows 11">
<img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+">
<img src="https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge" alt="License: MIT">
<img src="https://img.shields.io/badge/PyPI-v1.0-blue.svg?style=for-the-badge&logo=pypi&logoColor=white" alt="PyPI Package">

<br>
<br>

<p align="center">
  <img src="https://via.placeholder.com/800x400?text=AppBackup+Manager" alt="AppBackup Manager Hero Image" width="800">
</p>

**Effortlessly backup and restore your Windows application settings with a single command.**

</div>

---

## 🚀 Features

- **🔍 Smart App Detection** - Automatically scans and identifies all installed Windows applications
- **💾 Efficient Backups** - Creates highly compressed 7zip archives of app-specific user data
- **🏠 Home Directory Coverage** - Includes dot files and hidden directories in user's home folder
- **🔄 Version Management** - Maintains multiple backup versions with timestamps for each application
- **📝 Backup Notes** - Add and edit notes for each backup to track changes and configurations
- **🌓 Dark/Light Themes** - Modern, responsive UI with toggleable themes (dark mode by default)
- **🔄 Auto-Updates** - Seamlessly check for and install the latest version with one click
- **⚡ Rapid Development** - Cached scanning and dynamic UI loading for efficient iteration

## 📋 Overview

AppBackup Manager is a lightweight, user-friendly tool designed to simplify the backup and restoration of application-specific user settings and data on Windows 11. It targets tech-savvy users, IT professionals, and gamers who need a portable, efficient solution to preserve app configurations without full system backups.

Unlike general-purpose backup software, AppBackup Manager focuses exclusively on user settings and data tied to installed applications, offering a streamlined alternative for preserving your carefully customized application environments. It intelligently identifies and includes hidden configuration files (dot files) and directories in your home folder that many applications use to store settings.

## 🔧 Installation

Install with a single command:

```bash
pip install appbackup-manager && appbackup-manager
```

That's it! The application will launch in your default browser with a modern web interface.

## 📊 How It Works

<div align="center">
  <img src="https://via.placeholder.com/800x500?text=AppBackup+Manager+Interface" alt="AppBackup Manager Interface" width="800">
</div>

1. **Scan** - AppBackup Manager scans your system for installed applications
2. **Select** - Choose which applications you want to back up
3. **Backup** - Create compressed backups of your application settings
4. **Restore** - When needed, easily restore settings from any backup version

## 🔍 Key Use Cases

- **System Migration** - Transfer app settings to a new PC without reinstalling everything
- **Pre-Update Safety** - Back up app configurations before major updates or changes
- **Configuration Management** - Maintain different versions of app settings for various purposes
- **Gaming Profiles** - Preserve game saves and configurations between system resets

## 🛠️ Technical Details

AppBackup Manager is built with:

- **Python 3.8+** - Core application logic
- **Flask** - Web server and interface
- **py7zr** - 7zip compression library
- **Bootstrap/Tailwind** - Modern, responsive UI

The application creates two types of files:
- **`<appname>-<timestamp>.7z`** - Compressed backup of application data (including dot files)
- **`<appname>-<timestamp>.json`** - Metadata and user notes for the backup

AppBackup Manager intelligently handles:
- Standard application data folders (AppData\Local, AppData\Roaming)
- Hidden configuration files in the user's home directory
- Application-specific dot directories that follow Unix/Linux conventions

## 📈 Backup Statistics

| Feature | Specification |
|---------|---------------|
| Compression Ratio | Up to 90% size reduction |
| Scan Speed | <10 seconds on typical systems |
| Memory Usage | <200MB during operation |
| Supported OS | Windows 11 |

## 🔄 Updating

Update to the latest version with:

```bash
pip install --upgrade appbackup-manager
```

Or use the convenient update button in the application interface.

## 🧩 For Developers

AppBackup Manager supports rapid development with:

- Cached app scanning via `appscan.json`
- Dynamic UI loading from local templates
- Modular code structure (<500 lines per file)
- Comprehensive documentation

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

<div align="center">
  <p>Made with ❤️ for Windows power users</p>
  <p>© 2025 AppBackup Manager</p>
</div>