"""
ReformatBackup - Application Scanning

This module handles scanning for installed applications on Windows 11.
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Any, Optional
import winreg
import psutil

from reformatbackup.src.config import (
    get_scan_cache_path,
    get_auto_rescan,
    set_last_scan_time,
    get_last_scan_time
)

# Set up logging
logger = logging.getLogger(__name__)

def scan_installed_apps(force_rescan: bool = False) -> List[Dict[str, Any]]:
    """
    Scan for installed applications on Windows 11.
    
    Args:
        force_rescan (bool, optional): Whether to force a rescan of installed applications. Defaults to False.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing information about installed applications.
    """
    cache_path = get_scan_cache_path()
    auto_rescan = get_auto_rescan()
    last_scan_time = get_last_scan_time()
    
    # If auto_rescan is enabled and we haven't scanned in the last 24 hours, force a rescan
    if auto_rescan and last_scan_time:
        try:
            last_scan_datetime = datetime.datetime.strptime(last_scan_time, "%Y%m%d-%H%M%S")
            time_since_last_scan = datetime.datetime.now() - last_scan_datetime
            if time_since_last_scan.days >= 1:
                logger.info("Auto-rescan triggered: Last scan was more than 24 hours ago")
                force_rescan = True
        except Exception as e:
            logger.error(f"Error parsing last scan time: {e}")
    
    # Check if cache exists and we're not forcing a rescan
    if os.path.exists(cache_path) and not force_rescan:
        try:
            with open(cache_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
    
    # Scan for installed applications
    apps = []
    
    # Scan registry for installed applications
    try:
        apps.extend(_scan_registry())
    except Exception as e:
        logger.error(f"Error scanning registry: {e}")
    
    # Scan file system for installed applications
    try:
        apps.extend(_scan_file_system())
    except Exception as e:
        logger.error(f"Error scanning file system: {e}")
    
    # Scan for dot files in user home directory
    try:
        apps.extend(_scan_dot_files())
    except Exception as e:
        logger.error(f"Error scanning dot files: {e}")
    
    # Calculate sizes and add drive information
    for app in apps:
        if "path" in app and os.path.exists(app["path"]):
            app["size"] = _calculate_size(app["path"])
            app["drive"] = os.path.splitdrive(app["path"])[0]
    
    # Save to cache and update last scan time
    try:
        with open(cache_path, "w") as f:
            json.dump(apps, f)
        
        # Update last scan time
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        set_last_scan_time(timestamp)
        logger.info(f"Scan completed and cached at {timestamp}")
    except Exception as e:
        logger.error(f"Error saving cache: {e}")
    
    return apps

def _scan_registry() -> List[Dict[str, Any]]:
    """
    Scan the Windows registry for installed applications.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing information about installed applications.
    """
    apps = []
    
    # Registry paths to check
    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        # Add Microsoft Store apps
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\Repository\Packages"),
        # Add Windows Apps
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
    ]
    
    for hkey, path in registry_paths:
        try:
            key = winreg.OpenKey(hkey, path)
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    
                    try:
                        # For standard applications
                        if "Uninstall" in path:
                            name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            
                            # Skip entries without a name
                            if not name:
                                continue
                            
                            app = {"id": subkey_name, "name": name, "source": "registry"}
                            
                            # Get install location
                            try:
                                app["path"] = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                            except Exception:
                                pass
                            
                            # Get uninstall string
                            try:
                                app["uninstall"] = winreg.QueryValueEx(subkey, "UninstallString")[0]
                            except Exception:
                                pass
                            
                            # Get publisher
                            try:
                                app["publisher"] = winreg.QueryValueEx(subkey, "Publisher")[0]
                            except Exception:
                                pass
                            
                            # Get version
                            try:
                                app["version"] = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                            except Exception:
                                pass
                            
                            # Get install date
                            try:
                                app["install_date"] = winreg.QueryValueEx(subkey, "InstallDate")[0]
                            except Exception:
                                pass
                            
                        # For Microsoft Store apps
                        elif "Packages" in path:
                            # Use the package name as the display name if DisplayName is not available
                            app = {"id": f"msstore-{subkey_name}", "name": subkey_name, "source": "msstore"}
                            
                            try:
                                # Try to get a more user-friendly name
                                display_name_key = winreg.OpenKey(subkey, "DisplayName")
                                app["name"] = winreg.QueryValueEx(display_name_key, "")[0]
                                winreg.CloseKey(display_name_key)
                            except Exception:
                                # If we can't get a display name, clean up the package name
                                app["name"] = subkey_name.split('_')[0].replace('.', ' ')
                            
                            # Get package path
                            try:
                                path_key = winreg.OpenKey(subkey, "Path")
                                app["path"] = winreg.QueryValueEx(path_key, "")[0]
                                winreg.CloseKey(path_key)
                            except Exception:
                                pass
                        
                        # For Windows App Paths
                        elif "App Paths" in path:
                            app = {"id": f"apppath-{subkey_name}", "name": subkey_name, "source": "apppath"}
                            
                            # Get executable path
                            try:
                                app["path"] = winreg.QueryValueEx(subkey, "")[0]
                            except Exception:
                                pass
                        
                        apps.append(app)
                    except Exception as e:
                        logger.debug(f"Error processing registry key {subkey_name}: {e}")
                    
                    winreg.CloseKey(subkey)
                except Exception as e:
                    logger.debug(f"Error enumerating registry key {i}: {e}")
            
            winreg.CloseKey(key)
        except Exception as e:
            logger.debug(f"Error opening registry key {path}: {e}")
    
    # Remove duplicates based on name and path
    unique_apps = {}
    for app in apps:
        # Create a unique key based on name and path if available
        key = f"{app['name']}_{app.get('path', '')}"
        # Keep the entry with the most information
        if key not in unique_apps or len(app) > len(unique_apps[key]):
            unique_apps[key] = app
    
    return list(unique_apps.values())

def _scan_file_system() -> List[Dict[str, Any]]:
    """
    Scan the file system for installed applications.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing information about installed applications.
    """
    apps = []
    
    # Common installation directories
    install_dirs = [
        os.path.join(os.environ["ProgramFiles"]),
        os.path.join(os.environ["ProgramFiles(x86)"]),
        os.path.join(os.environ["LOCALAPPDATA"], "Programs"),
        os.path.join(os.environ["APPDATA"]),
        os.path.join(os.environ["LOCALAPPDATA"]),
        # Add Steam games directory if it exists
        os.path.join(os.environ["ProgramFiles(x86)"], "Steam", "steamapps", "common"),
        os.path.join(os.environ["ProgramFiles"], "Steam", "steamapps", "common"),
        # Add Epic Games directory if it exists
        os.path.join(os.environ["ProgramFiles"], "Epic Games"),
        # Add GOG Games directory if it exists
        os.path.join(os.environ["ProgramFiles"], "GOG Galaxy", "Games"),
    ]
    
    # Filter out non-existent directories
    install_dirs = [d for d in install_dirs if os.path.exists(d)]
    
    # Add all drive roots to scan for game installations
    for drive in _get_available_drives():
        game_dirs = [
            os.path.join(drive, "Games"),
            os.path.join(drive, "SteamLibrary", "steamapps", "common"),
            os.path.join(drive, "Epic Games"),
            os.path.join(drive, "GOG Games"),
        ]
        install_dirs.extend([d for d in game_dirs if os.path.exists(d)])
    
    for install_dir in install_dirs:
        try:
            for app_dir in os.listdir(install_dir):
                app_path = os.path.join(install_dir, app_dir)
                if os.path.isdir(app_path):
                    # Skip system directories and hidden directories
                    if app_dir.startswith('.') or app_dir in ["Windows", "Program Files", "Program Files (x86)", "Users", "ProgramData"]:
                        continue
                    
                    # Check if this is likely an application by looking for executables
                    is_app = False
                    exe_path = None
                    
                    # Look for .exe files directly in the directory
                    for file in os.listdir(app_path):
                        if file.endswith(".exe") and not file.startswith("unins"):
                            is_app = True
                            exe_path = os.path.join(app_path, file)
                            break
                    
                    # If no .exe found, look in bin or similar subdirectories
                    if not is_app:
                        for subdir in ["bin", "program", "app"]:
                            subdir_path = os.path.join(app_path, subdir)
                            if os.path.exists(subdir_path) and os.path.isdir(subdir_path):
                                for file in os.listdir(subdir_path):
                                    if file.endswith(".exe") and not file.startswith("unins"):
                                        is_app = True
                                        exe_path = os.path.join(subdir_path, file)
                                        break
                    
                    if is_app:
                        app_id = app_dir.lower().replace(" ", "-")
                        app_info = {
                            "id": f"fs-{app_id}",
                            "name": app_dir,
                            "path": app_path,
                            "source": "file_system",
                        }
                        
                        if exe_path:
                            app_info["executable"] = exe_path
                        
                        apps.append(app_info)
        except Exception as e:
            logger.debug(f"Error scanning directory {install_dir}: {e}")
    
    return apps

def _get_available_drives() -> List[str]:
    """
    Get a list of available drive letters on Windows.
    
    Returns:
        List[str]: A list of drive letters with trailing backslash (e.g., ["C:\\", "D:\\"])
    """
    drives = []
    
    try:
        # Get all logical drives
        for drive in range(ord('A'), ord('Z') + 1):
            drive_letter = chr(drive) + ":\\"
            if os.path.exists(drive_letter):
                drives.append(drive_letter)
    except Exception as e:
        logger.error(f"Error getting available drives: {e}")
        # Fallback to common drives
        drives = ["C:\\"]
    
    return drives

def _scan_dot_files() -> List[Dict[str, Any]]:
    """
    Scan for dot files and application-specific directories in the user's home directory.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing information about dot files and app data.
    """
    apps = []
    
    home_dir = os.path.expanduser("~")
    
    # Common application data directories to check
    app_data_dirs = {
        ".vscode": "Visual Studio Code",
        ".atom": "Atom Editor",
        ".config": "Configuration Files",
        ".ssh": "SSH Configuration",
        ".aws": "AWS CLI Configuration",
        ".docker": "Docker Configuration",
        ".npm": "NPM Configuration",
        ".gradle": "Gradle Configuration",
        ".m2": "Maven Configuration",
        ".android": "Android SDK Configuration",
        ".bash_history": "Bash History",
        ".zsh_history": "Zsh History",
        ".bashrc": "Bash Configuration",
        ".zshrc": "Zsh Configuration",
        ".gitconfig": "Git Configuration",
        ".profile": "Shell Profile",
        ".vim": "Vim Configuration",
        ".vimrc": "Vim Configuration",
        ".emacs.d": "Emacs Configuration",
        ".mozilla": "Mozilla Firefox Data",
        ".thunderbird": "Thunderbird Data",
        ".config/google-chrome": "Google Chrome Data",
        ".config/chromium": "Chromium Data",
        ".config/Code": "VS Code Configuration",
        ".config/discord": "Discord Configuration",
        ".config/spotify": "Spotify Configuration",
        ".config/slack": "Slack Configuration",
        ".config/teams": "Microsoft Teams Configuration",
    }
    
    # Scan for dot files and directories
    for item in os.listdir(home_dir):
        item_path = os.path.join(home_dir, item)
        
        # Process dot files and directories
        if item.startswith("."):
            # Skip git directories and common system directories
            if item in [".git", ".cache", ".local"] or item.startswith(".git"):
                continue
            
            # Check if this is a known application data directory
            app_name = app_data_dirs.get(item, f"Dot File: {item}")
            
            apps.append({
                "id": f"dotfile-{item[1:]}",
                "name": app_name,
                "path": item_path,
                "source": "dot_file",
                "type": "configuration" if os.path.isdir(item_path) else "file"
            })
    
    # Scan AppData directories for application data
    appdata_dirs = [
        os.path.join(os.environ["APPDATA"]),
        os.path.join(os.environ["LOCALAPPDATA"]),
    ]
    
    for appdata_dir in appdata_dirs:
        if os.path.exists(appdata_dir):
            try:
                for app_dir in os.listdir(appdata_dir):
                    app_path = os.path.join(appdata_dir, app_dir)
                    if os.path.isdir(app_path):
                        # Skip system directories
                        if app_dir in ["Microsoft", "Windows", "Temp", "History", "Packages"]:
                            continue
                        
                        apps.append({
                            "id": f"appdata-{app_dir.lower().replace(' ', '-')}",
                            "name": f"App Data: {app_dir}",
                            "path": app_path,
                            "source": "app_data",
                            "type": "user_data"
                        })
            except Exception as e:
                logger.debug(f"Error scanning AppData directory {appdata_dir}: {e}")
    
    return apps

def _calculate_size(path: str) -> int:
    """
    Calculate the size of a directory or file.
    
    Args:
        path (str): The path to the directory or file.
    
    Returns:
        int: The size in bytes.
    """
    if not os.path.exists(path):
        return 0
    
    if os.path.isfile(path):
        try:
            return os.path.getsize(path)
        except Exception as e:
            logger.debug(f"Error getting size of file {path}: {e}")
            return 0
    
    total_size = 0
    try:
        # Use psutil for faster disk usage calculation if available
        if hasattr(psutil, 'disk_usage'):
            try:
                return psutil.disk_usage(path).used
            except:
                # Fall back to manual calculation
                pass
        
        # Manual calculation
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    # Skip symbolic links to avoid infinite loops
                    if not os.path.islink(file_path):
                        total_size += os.path.getsize(file_path)
                except Exception as e:
                    logger.debug(f"Error getting size of file {file_path}: {e}")
    except Exception as e:
        logger.debug(f"Error walking directory {path}: {e}")
    
    return total_size