"""
ReformatBackup - Restore Functionality

This module handles restoring application data from backups.
"""

import os
import json
import logging
import datetime
import shutil
from typing import Dict, Any, List, Optional
import py7zr

# Set up logging
logger = logging.getLogger(__name__)

def get_backup_versions(app_id: str) -> List[Dict[str, Any]]:
    """
    Get a list of backup versions for an application.
    
    Args:
        app_id (str): The ID of the application to get backup versions for.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing information about backup versions.
    """
    from reformatbackup.src.backup import get_backup_location
    
    # Get the backup location
    backup_location = get_backup_location()
    
    # Find all backup files for the application
    versions = []
    
    if os.path.exists(backup_location):
        for filename in os.listdir(backup_location):
            if filename.startswith(f"{app_id}-") and filename.endswith(".7z"):
                # Extract the timestamp from the filename
                timestamp = filename[len(app_id) + 1:-3]
                
                # Create the backup ID
                backup_id = f"{app_id}-{timestamp}"
                
                # Get the metadata file path
                metadata_path = os.path.join(backup_location, f"{backup_id}.json")
                
                # Load the metadata if it exists
                metadata = {}
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, "r") as f:
                            metadata = json.load(f)
                    except Exception as e:
                        logger.error(f"Error loading metadata: {e}")
                
                # Get the backup file path
                backup_path = os.path.join(backup_location, filename)
                
                # Get the backup size
                size = os.path.getsize(backup_path) if os.path.exists(backup_path) else 0
                
                # Add the version to the list
                versions.append({
                    "backup_id": backup_id,
                    "timestamp": timestamp,
                    "backup_path": backup_path,
                    "metadata_path": metadata_path,
                    "size": size,
                    "notes": metadata.get("notes", ""),
                })
    
    # Sort versions by timestamp (newest first)
    versions.sort(key=lambda v: v["timestamp"], reverse=True)
    
    return versions

def get_backup_details(backup_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a backup.
    
    Args:
        backup_id (str): The ID of the backup to get details for.
    
    Returns:
        Dict[str, Any]: A dictionary containing detailed information about the backup.
    """
    from reformatbackup.src.backup import get_backup_location
    
    # Get the backup location
    backup_location = get_backup_location()
    
    # Get the backup file path
    backup_path = os.path.join(backup_location, f"{backup_id}.7z")
    
    if not os.path.exists(backup_path):
        return {"success": False, "error": f"Backup file not found: {backup_path}"}
    
    # Get the metadata file path
    metadata_path = os.path.join(backup_location, f"{backup_id}.json")
    
    # Load the metadata if it exists
    metadata = {}
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return {"success": False, "error": f"Error loading metadata: {e}"}
    
    # Get the backup size
    size = os.path.getsize(backup_path) if os.path.exists(backup_path) else 0
    
    # Format the timestamp
    timestamp = metadata.get("timestamp", "")
    if timestamp:
        try:
            dt = datetime.datetime.strptime(timestamp, "%Y%m%d-%H%M%S")
            formatted_timestamp = dt.strftime("%B %d, %Y at %I:%M %p")
        except Exception:
            formatted_timestamp = timestamp
    else:
        formatted_timestamp = "Unknown"
    
    # Return the details
    return {
        "success": True,
        "backup_id": backup_id,
        "app_id": metadata.get("app_id", ""),
        "app_name": metadata.get("app_name", ""),
        "timestamp": formatted_timestamp,
        "size": f"{size / (1024 * 1024):.2f} MB" if size > 0 else "0 B",
        "notes": metadata.get("notes", ""),
        "paths": metadata.get("paths", []),
        "compression_level": metadata.get("compression_level", 9),
        "backup_dot_files": metadata.get("backup_dot_files", False),
    }

def restore_backup(app_id: str, backup_id: str, backup_first: bool = False,
                  restore_dot_files: bool = False, conflict_resolution: str = "overwrite-all") -> Dict[str, Any]:
    """
    Restore an application's data from a backup.
    
    Args:
        app_id (str): The ID of the application to restore.
        backup_id (str): The ID of the backup to restore.
        backup_first (bool, optional): Whether to back up the current state before restoring. Defaults to False.
        restore_dot_files (bool, optional): Whether to restore dot files. Defaults to False.
        conflict_resolution (str, optional): How to handle file conflicts.
            Options: "overwrite-all", "keep-newer", "ask". Defaults to "overwrite-all".
    
    Returns:
        Dict[str, Any]: A dictionary containing information about the restore operation.
    """
    from reformatbackup.src.scan import scan_installed_apps
    from reformatbackup.src.backup import backup_app, get_backup_location
    
    # Get the backup location
    backup_location = get_backup_location()
    
    # Get the backup file path
    backup_path = os.path.join(backup_location, f"{backup_id}.7z")
    
    if not os.path.exists(backup_path):
        return {"success": False, "error": f"Backup file not found: {backup_path}"}
    
    # Get the metadata file path
    metadata_path = os.path.join(backup_location, f"{backup_id}.json")
    
    # Load the metadata if it exists
    metadata = {}
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
    
    # Get the list of installed applications
    apps = scan_installed_apps()
    
    # Find the application to restore
    app = None
    for a in apps:
        if a.get("id") == app_id:
            app = a
            break
    
    if not app:
        return {"success": False, "error": f"Application with ID {app_id} not found"}
    
    # Back up the current state if requested
    if backup_first:
        backup_result = backup_app(app_id)
        if not backup_result.get("success", False):
            return {"success": False, "error": f"Error backing up current state: {backup_result.get('error', 'Unknown error')}"}
    
    # Determine the paths to restore to
    paths_to_restore = []
    
    # Add the application path if it exists
    if "path" in app and os.path.exists(app["path"]):
        paths_to_restore.append(app["path"])
    
    # Add AppData paths
    appdata_paths = [
        os.path.join(os.environ["APPDATA"], app.get("name", "")),
        os.path.join(os.environ["LOCALAPPDATA"], app.get("name", "")),
    ]
    
    for path in appdata_paths:
        if os.path.exists(path):
            paths_to_restore.append(path)
    
    # Add dot files if this is a dot file backup or if restore_dot_files is enabled
    if (app.get("source") == "dot_file" and "path" in app) or restore_dot_files:
        # If this is a dot file app, add its path
        if app.get("source") == "dot_file" and "path" in app:
            paths_to_restore.append(app["path"])
        
        # If restore_dot_files is enabled, look for additional dot files related to this app
        if restore_dot_files:
            # Look for dot files in the user's home directory that might be related to this app
            home_dir = os.path.expanduser("~")
            app_name_lower = app.get("name", "").lower()
            
            # Common patterns for dot files
            patterns = [
                f".{app_name_lower}",
                f".{app_name_lower}rc",
                f".{app_name_lower}.json",
                f".{app_name_lower}.yaml",
                f".{app_name_lower}.yml",
                f".{app_name_lower}.config",
                f".{app_name_lower}.conf",
                f".config/{app_name_lower}"
            ]
            
            for pattern in patterns:
                dot_file_path = os.path.join(home_dir, pattern)
                if os.path.exists(dot_file_path):
                    paths_to_restore.append(dot_file_path)
    
    # If no paths to restore to, return an error
    if not paths_to_restore:
        return {"success": False, "error": f"No data found to restore for {app.get('name', app_id)}"}
    
    # Create a temporary directory for extraction
    temp_dir = os.path.join(os.environ["TEMP"], f"reformatbackup_{app_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
    
    try:
        os.makedirs(temp_dir)
    except Exception as e:
        logger.error(f"Error creating temporary directory: {e}")
        return {"success": False, "error": f"Error creating temporary directory: {e}"}
    
    # Extract the backup to the temporary directory
    try:
        with py7zr.SevenZipFile(backup_path, mode="r") as archive:
            archive.extractall(temp_dir)
    except Exception as e:
        logger.error(f"Error extracting backup: {e}")
        return {"success": False, "error": f"Error extracting backup: {e}"}
    
    # Restore the files to their original locations
    restored_files = 0
    skipped_files = 0
    error_files = 0
    
    for path in paths_to_restore:
        try:
            # Get the directory name
            dir_name = os.path.basename(path)
            
            # Find the corresponding directory in the temporary directory
            temp_path = os.path.join(temp_dir, dir_name)
            
            if os.path.exists(temp_path):
                # Create the directory if it doesn't exist
                os.makedirs(path, exist_ok=True)
                
                # Copy the files based on conflict resolution strategy
                for root, dirs, files in os.walk(temp_path):
                    # Create subdirectories
                    for dir in dirs:
                        dir_path = os.path.join(path, os.path.relpath(os.path.join(root, dir), temp_path))
                        os.makedirs(dir_path, exist_ok=True)
                    
                    # Copy files
                    for file in files:
                        src = os.path.join(root, file)
                        dst = os.path.join(path, os.path.relpath(src, temp_path))
                        
                        # Handle file conflicts based on the selected strategy
                        if os.path.exists(dst):
                            if conflict_resolution == "overwrite-all":
                                # Overwrite the existing file
                                shutil.copy2(src, dst)
                                restored_files += 1
                            elif conflict_resolution == "keep-newer":
                                # Compare modification times
                                src_mtime = os.path.getmtime(src)
                                dst_mtime = os.path.getmtime(dst)
                                
                                if src_mtime > dst_mtime:
                                    # Backup file is newer, overwrite
                                    shutil.copy2(src, dst)
                                    restored_files += 1
                                else:
                                    # Existing file is newer, keep it
                                    skipped_files += 1
                            elif conflict_resolution == "ask":
                                # In a real implementation, this would prompt the user
                                # For now, we'll just overwrite
                                shutil.copy2(src, dst)
                                restored_files += 1
                        else:
                            # No conflict, just copy the file
                            os.makedirs(os.path.dirname(dst), exist_ok=True)
                            shutil.copy2(src, dst)
                            restored_files += 1
        except Exception as e:
            logger.error(f"Error restoring files: {e}")
            error_files += 1
    
    # Clean up the temporary directory
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        logger.error(f"Error cleaning up temporary directory: {e}")
    
    return {
        "success": True,
        "app_id": app_id,
        "app_name": app.get("name", app_id),
        "backup_id": backup_id,
        "backup_path": backup_path,
        "metadata_path": metadata_path,
        "timestamp": metadata.get("timestamp", ""),
        "restored_files": restored_files,
        "skipped_files": skipped_files,
        "error_files": error_files,
        "restore_dot_files": restore_dot_files,
        "conflict_resolution": conflict_resolution
    }
def restore_dot_files(backup_id: str, conflict_resolution: str = "overwrite-all") -> Dict[str, Any]:
    """
    Restore dot files from a backup.
    
    Args:
        backup_id (str): The ID of the backup to restore.
        conflict_resolution (str, optional): How to handle file conflicts.
            Options: "overwrite-all", "keep-newer", "ask". Defaults to "overwrite-all".
    
    Returns:
        Dict[str, Any]: A dictionary containing information about the restore operation.
    """
    # Extract the app_id from the backup_id
    app_id = backup_id.split("-")[0]
    
    # This is a specialized version of restore_backup for dot files
    return restore_backup(app_id, backup_id, restore_dot_files=True, conflict_resolution=conflict_resolution)
    return restore_backup(app_id, backup_id)

def backup_then_restore(app_id: str, backup_id: str) -> Dict[str, Any]:
    """
    Back up the current state of an application, then restore from a backup.
    
    Args:
        app_id (str): The ID of the application to restore.
        backup_id (str): The ID of the backup to restore.
    
    Returns:
        Dict[str, Any]: A dictionary containing information about the restore operation.
    """
    return restore_backup(app_id, backup_id, backup_first=True)