"""
ReformatBackup - Backup Functionality

This module handles backing up application data.
"""

import os
import json
import logging
import datetime
from typing import Dict, Any, List, Optional
import py7zr

# Set up logging
logger = logging.getLogger(__name__)

def get_config_path() -> str:
    """
    Get the path to the configuration file.
    
    Returns:
        str: The path to the configuration file.
    """
    return os.path.join(os.path.expanduser("~"), ".reformatbackup")

def get_backup_location() -> str:
    """
    Get the backup location from the configuration file.
    
    Returns:
        str: The backup location.
    """
    config_path = get_config_path()
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                return config.get("backup_location", os.path.join(os.path.expanduser("~"), "Backups"))
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    # Default backup location
    default_location = os.path.join(os.path.expanduser("~"), "Backups")
    
    # Create the default backup location if it doesn't exist
    if not os.path.exists(default_location):
        try:
            os.makedirs(default_location)
        except Exception as e:
            logger.error(f"Error creating default backup location: {e}")
    
    # Save the default backup location to the configuration file
    set_backup_location(default_location)
    
    return default_location

def set_backup_location(location: str) -> bool:
    """
    Set the backup location in the configuration file.
    
    Args:
        location (str): The backup location.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    config_path = get_config_path()
    
    # Create the backup location if it doesn't exist
    if not os.path.exists(location):
        try:
            os.makedirs(location)
        except Exception as e:
            logger.error(f"Error creating backup location: {e}")
            return False
    
    # Load existing configuration if it exists
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    # Update the backup location
    config["backup_location"] = location
    
    # Save the configuration
    try:
        with open(config_path, "w") as f:
            json.dump(config, f)
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        return False

def backup_app(app_id: str) -> Dict[str, Any]:
    """
    Back up an application's data.
    
    Args:
        app_id (str): The ID of the application to back up.
    
    Returns:
        Dict[str, Any]: A dictionary containing information about the backup.
    """
    from reformatbackup.src.scan import scan_installed_apps
    
    # Get the list of installed applications
    apps = scan_installed_apps()
    
    # Find the application to back up
    app = None
    for a in apps:
        if a.get("id") == app_id:
            app = a
            break
    
    if not app:
        return {"success": False, "error": f"Application with ID {app_id} not found"}
    
    # Get the backup location
    backup_location = get_backup_location()
    
    # Create a timestamp for the backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # Create the backup filename
    backup_filename = f"{app_id}-{timestamp}.7z"
    backup_path = os.path.join(backup_location, backup_filename)
    
    # Create the metadata filename
    metadata_filename = f"{app_id}-{timestamp}.json"
    metadata_path = os.path.join(backup_location, metadata_filename)
    
    # Determine the paths to back up
    paths_to_backup = []
    
    # Add the application path if it exists
    if "path" in app and os.path.exists(app["path"]):
        paths_to_backup.append(app["path"])
    
    # Add AppData paths
    appdata_paths = [
        os.path.join(os.environ["APPDATA"], app.get("name", "")),
        os.path.join(os.environ["LOCALAPPDATA"], app.get("name", "")),
    ]
    
    for path in appdata_paths:
        if os.path.exists(path):
            paths_to_backup.append(path)
    
    # Add dot files if this is a dot file backup
    if app.get("source") == "dot_file" and "path" in app:
        paths_to_backup.append(app["path"])
    
    # If no paths to backup, return an error
    if not paths_to_backup:
        return {"success": False, "error": f"No data found to back up for {app.get('name', app_id)}"}
    
    # Create the backup
    try:
        with py7zr.SevenZipFile(backup_path, mode="w", filters=[{"id": py7zr.FILTER_LZMA2, "preset": 9}]) as archive:
            for path in paths_to_backup:
                if os.path.isdir(path):
                    # Add directory contents
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                # Calculate the archive path (relative to the backup root)
                                arcname = os.path.relpath(file_path, os.path.dirname(path))
                                archive.write(file_path, arcname)
                            except Exception as e:
                                logger.error(f"Error adding file to archive: {e}")
                else:
                    # Add file
                    try:
                        archive.write(path, os.path.basename(path))
                    except Exception as e:
                        logger.error(f"Error adding file to archive: {e}")
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return {"success": False, "error": str(e)}
    
    # Create the metadata
    metadata = {
        "app_id": app_id,
        "app_name": app.get("name", app_id),
        "timestamp": timestamp,
        "paths": paths_to_backup,
        "size": os.path.getsize(backup_path) if os.path.exists(backup_path) else 0,
        "notes": "",
    }
    
    # Save the metadata
    try:
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)
    except Exception as e:
        logger.error(f"Error saving metadata: {e}")
    
    return {
        "success": True,
        "app_id": app_id,
        "app_name": app.get("name", app_id),
        "backup_path": backup_path,
        "metadata_path": metadata_path,
        "timestamp": timestamp,
        "size": os.path.getsize(backup_path) if os.path.exists(backup_path) else 0,
    }

def backup_dot_files(app_id: str) -> Dict[str, Any]:
    """
    Back up dot files for an application.
    
    Args:
        app_id (str): The ID of the application to back up dot files for.
    
    Returns:
        Dict[str, Any]: A dictionary containing information about the backup.
    """
    # This is a specialized version of backup_app for dot files
    return backup_app(app_id)

def add_notes(backup_id: str, notes: str) -> bool:
    """
    Add notes to a backup.
    
    Args:
        backup_id (str): The ID of the backup to add notes to.
        notes (str): The notes to add.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    backup_location = get_backup_location()
    
    # Find the metadata file
    metadata_path = os.path.join(backup_location, f"{backup_id}.json")
    
    if not os.path.exists(metadata_path):
        logger.error(f"Metadata file not found: {metadata_path}")
        return False
    
    # Load the metadata
    try:
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    except Exception as e:
        logger.error(f"Error loading metadata: {e}")
        return False
    
    # Update the notes
    metadata["notes"] = notes
    
    # Save the metadata
    try:
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)
        return True
    except Exception as e:
        logger.error(f"Error saving metadata: {e}")
        return False