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

from reformatbackup.src.config import (
    get_backup_location,
    set_backup_location,
    get_compression_level,
    get_max_backups_per_app
)

# Set up logging
logger = logging.getLogger(__name__)

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
        compression_level = get_compression_level()
        with py7zr.SevenZipFile(backup_path, mode="w", filters=[{"id": py7zr.FILTER_LZMA2, "preset": compression_level}]) as archive:
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
    
    # Clean up old backups if we exceed the maximum number of backups per app
    max_backups = get_max_backups_per_app()
    cleanup_old_backups(app_id, max_backups)
    
    return {
        "success": True,
        "app_id": app_id,
        "app_name": app.get("name", app_id),
        "backup_path": backup_path,
        "metadata_path": metadata_path,
        "timestamp": timestamp,
        "size": os.path.getsize(backup_path) if os.path.exists(backup_path) else 0,
    }
    
def cleanup_old_backups(app_id: str, max_backups: int) -> None:
    """
    Clean up old backups for an application if we exceed the maximum number of backups.
    
    Args:
        app_id (str): The ID of the application.
        max_backups (int): The maximum number of backups to keep.
    """
    backup_location = get_backup_location()
    
    # Find all backups for this application
    backups = []
    for filename in os.listdir(backup_location):
        if filename.startswith(f"{app_id}-") and filename.endswith(".7z"):
            backup_path = os.path.join(backup_location, filename)
            metadata_path = os.path.join(backup_location, filename.replace(".7z", ".json"))
            timestamp = filename.split("-")[1].split(".")[0] if "-" in filename else ""
            
            backups.append({
                "backup_path": backup_path,
                "metadata_path": metadata_path,
                "timestamp": timestamp
            })
    
    # Sort backups by timestamp (newest first)
    backups.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Remove old backups if we exceed the maximum
    if len(backups) > max_backups:
        for backup in backups[max_backups:]:
            try:
                if os.path.exists(backup["backup_path"]):
                    os.remove(backup["backup_path"])
                    logger.info(f"Removed old backup: {backup['backup_path']}")
                
                if os.path.exists(backup["metadata_path"]):
                    os.remove(backup["metadata_path"])
                    logger.info(f"Removed old metadata: {backup['metadata_path']}")
            except Exception as e:
                logger.error(f"Error removing old backup: {e}")

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