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
    ]
    
    for hkey, path in registry_paths:
        try:
            key = winreg.OpenKey(hkey, path)
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    
                    try:
                        name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        
                        # Skip entries without a name
                        if not name:
                            continue
                        
                        app = {"id": subkey_name, "name": name, "source": "registry"}
                        
                        # Get install location
                        try:
                            app["path"] = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                        except:
                            pass
                        
                        # Get uninstall string
                        try:
                            app["uninstall"] = winreg.QueryValueEx(subkey, "UninstallString")[0]
                        except:
                            pass
                        
                        apps.append(app)
                    except:
                        pass
                    
                    winreg.CloseKey(subkey)
                except:
                    pass
            
            winreg.CloseKey(key)
        except:
            pass
    
    return apps

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
    ]
    
    for install_dir in install_dirs:
        if os.path.exists(install_dir):
            for app_dir in os.listdir(install_dir):
                app_path = os.path.join(install_dir, app_dir)
                if os.path.isdir(app_path):
                    apps.append({
                        "id": app_dir.lower().replace(" ", "-"),
                        "name": app_dir,
                        "path": app_path,
                        "source": "file_system",
                    })
    
    return apps

def _scan_dot_files() -> List[Dict[str, Any]]:
    """
    Scan for dot files in the user's home directory.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing information about dot files.
    """
    apps = []
    
    home_dir = os.path.expanduser("~")
    
    for item in os.listdir(home_dir):
        if item.startswith(".") and not item.startswith(".git"):
            item_path = os.path.join(home_dir, item)
            
            # Skip common system dot files
            if item in [".cache", ".config", ".local"]:
                continue
            
            apps.append({
                "id": f"dotfile-{item[1:]}",
                "name": f"Dot File: {item}",
                "path": item_path,
                "source": "dot_file",
            })
    
    return apps

def _calculate_size(path: str) -> int:
    """
    Calculate the size of a directory or file.
    
    Args:
        path (str): The path to the directory or file.
    
    Returns:
        int: The size in bytes.
    """
    if os.path.isfile(path):
        return os.path.getsize(path)
    
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(file_path)
            except:
                pass
    
    return total_size