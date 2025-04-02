"""
ReformatBackup - Configuration Management

This module handles reading and writing configuration settings for the application.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union

# Set up logging
logger = logging.getLogger(__name__)

# Default configuration values
DEFAULT_CONFIG = {
    "backup_location": os.path.join(os.path.expanduser("~"), "Backups"),
    "auto_rescan": True,
    "theme": "dark",
    "check_updates": True,
    "max_backups_per_app": 10,
    "compression_level": 9,
    "backup_dot_files": True,
    "last_scan_time": None,
}

def get_config_path() -> str:
    """
    Get the path to the configuration file.
    
    Returns:
        str: The path to the configuration file.
    """
    return os.path.join(os.path.expanduser("~"), ".reformatbackup")

def get_config() -> Dict[str, Any]:
    """
    Get the configuration settings.
    
    Returns:
        Dict[str, Any]: The configuration settings.
    """
    config_path = get_config_path()
    
    # If the configuration file exists, load it
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                
                # Merge with default config to ensure all keys exist
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                        
                return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    # If the configuration file doesn't exist or couldn't be loaded,
    # create it with default values
    try:
        # Ensure the parent directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Write the default configuration
        with open(config_path, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        
        return DEFAULT_CONFIG.copy()
    except Exception as e:
        logger.error(f"Error creating default configuration: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> bool:
    """
    Save the configuration settings.
    
    Args:
        config (Dict[str, Any]): The configuration settings to save.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    config_path = get_config_path()
    
    try:
        # Ensure the parent directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Write the configuration
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        return False

def update_config(key: str, value: Any) -> bool:
    """
    Update a specific configuration setting.
    
    Args:
        key (str): The configuration key to update.
        value (Any): The new value for the configuration key.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    config = get_config()
    config[key] = value
    return save_config(config)

def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get a specific configuration value.
    
    Args:
        key (str): The configuration key to get.
        default (Any, optional): The default value to return if the key doesn't exist.
            Defaults to None.
    
    Returns:
        Any: The configuration value, or the default if the key doesn't exist.
    """
    config = get_config()
    return config.get(key, default)

def get_backup_location() -> str:
    """
    Get the backup location from the configuration.
    
    Returns:
        str: The backup location.
    """
    location = get_config_value("backup_location")
    
    # Create the backup location if it doesn't exist
    if not os.path.exists(location):
        try:
            os.makedirs(location)
            logger.info(f"Created backup location: {location}")
        except Exception as e:
            logger.error(f"Error creating backup location: {e}")
            # Fall back to the default location
            location = DEFAULT_CONFIG["backup_location"]
            if not os.path.exists(location):
                try:
                    os.makedirs(location)
                except Exception as e:
                    logger.error(f"Error creating default backup location: {e}")
    
    return location

def set_backup_location(location: str) -> bool:
    """
    Set the backup location in the configuration.
    
    Args:
        location (str): The backup location.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    # Create the backup location if it doesn't exist
    if not os.path.exists(location):
        try:
            os.makedirs(location)
            logger.info(f"Created backup location: {location}")
        except Exception as e:
            logger.error(f"Error creating backup location: {e}")
            return False
    
    return update_config("backup_location", location)

def get_scan_cache_path() -> str:
    """
    Get the path to the scan cache file.
    
    Returns:
        str: The path to the scan cache file.
    """
    return os.path.join(os.path.expanduser("~"), "appscan.json")

def get_auto_rescan() -> bool:
    """
    Get whether to automatically rescan on startup.
    
    Returns:
        bool: True if auto-rescan is enabled, False otherwise.
    """
    return get_config_value("auto_rescan", DEFAULT_CONFIG["auto_rescan"])

def set_auto_rescan(enabled: bool) -> bool:
    """
    Set whether to automatically rescan on startup.
    
    Args:
        enabled (bool): Whether to enable auto-rescan.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    return update_config("auto_rescan", enabled)

def get_theme() -> str:
    """
    Get the UI theme.
    
    Returns:
        str: The theme name ("light" or "dark").
    """
    return get_config_value("theme", DEFAULT_CONFIG["theme"])

def set_theme(theme: str) -> bool:
    """
    Set the UI theme.
    
    Args:
        theme (str): The theme name ("light" or "dark").
    
    Returns:
        bool: True if successful, False otherwise.
    """
    if theme not in ["light", "dark"]:
        logger.error(f"Invalid theme: {theme}")
        return False
    
    return update_config("theme", theme)

def get_check_updates() -> bool:
    """
    Get whether to check for updates on startup.
    
    Returns:
        bool: True if update checking is enabled, False otherwise.
    """
    return get_config_value("check_updates", DEFAULT_CONFIG["check_updates"])

def set_check_updates(enabled: bool) -> bool:
    """
    Set whether to check for updates on startup.
    
    Args:
        enabled (bool): Whether to enable update checking.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    return update_config("check_updates", enabled)

def get_max_backups_per_app() -> int:
    """
    Get the maximum number of backups to keep per application.
    
    Returns:
        int: The maximum number of backups.
    """
    return get_config_value("max_backups_per_app", DEFAULT_CONFIG["max_backups_per_app"])

def set_max_backups_per_app(max_backups: int) -> bool:
    """
    Set the maximum number of backups to keep per application.
    
    Args:
        max_backups (int): The maximum number of backups.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    if max_backups < 1:
        logger.error(f"Invalid max_backups: {max_backups}")
        return False
    
    return update_config("max_backups_per_app", max_backups)

def get_compression_level() -> int:
    """
    Get the compression level for backups.
    
    Returns:
        int: The compression level (0-9).
    """
    return get_config_value("compression_level", DEFAULT_CONFIG["compression_level"])

def set_compression_level(level: int) -> bool:
    """
    Set the compression level for backups.
    
    Args:
        level (int): The compression level (0-9).
    
    Returns:
        bool: True if successful, False otherwise.
    """
    if level < 0 or level > 9:
        logger.error(f"Invalid compression level: {level}")
        return False
    
    return update_config("compression_level", level)

def get_backup_dot_files() -> bool:
    """
    Get whether to back up dot files.
    
    Returns:
        bool: True if dot file backup is enabled, False otherwise.
    """
    return get_config_value("backup_dot_files", DEFAULT_CONFIG["backup_dot_files"])

def set_backup_dot_files(enabled: bool) -> bool:
    """
    Set whether to back up dot files.
    
    Args:
        enabled (bool): Whether to enable dot file backup.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    return update_config("backup_dot_files", enabled)

def get_last_scan_time() -> Optional[str]:
    """
    Get the timestamp of the last scan.
    
    Returns:
        Optional[str]: The timestamp of the last scan, or None if no scan has been performed.
    """
    return get_config_value("last_scan_time")

def set_last_scan_time(timestamp: str) -> bool:
    """
    Set the timestamp of the last scan.
    
    Args:
        timestamp (str): The timestamp of the last scan.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    return update_config("last_scan_time", timestamp)