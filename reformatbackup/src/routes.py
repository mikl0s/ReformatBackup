"""
ReformatBackup - Routes

This module defines the Flask routes for the ReformatBackup application.
"""

import os
import logging
from typing import Any, Dict, List, Optional

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, current_app

from reformatbackup.src.config import (
    get_check_updates,
    set_check_updates
)

# Set up logging
logger = logging.getLogger(__name__)

# Type definitions for better type hinting
AppInfo = Dict[str, Any]
BackupInfo = Dict[str, Any]

def calculate_drive_sizes(apps: List[AppInfo]) -> Dict[str, int]:
    """
    Calculate the total size of applications per drive.
    
    Args:
        apps (List[AppInfo]): The list of applications.
        
    Returns:
        Dict[str, int]: A dictionary mapping drive letters to total sizes.
    """
    drive_sizes = {}
    for app in apps:
        drive = app.get('drive', 'Unknown')
        size = app.get('size', 0)
        if drive in drive_sizes:
            drive_sizes[drive] += size
        else:
            drive_sizes[drive] = size
    return drive_sizes

def get_recent_backups(limit: int = 5) -> List[BackupInfo]:
    """
    Get a list of recent backups.
    
    Args:
        limit (int, optional): The maximum number of backups to return. Defaults to 5.
        
    Returns:
        List[BackupInfo]: A list of recent backup information.
    """
    # This is a placeholder - in a real implementation, this would query
    # the backup directory for recent backups
    # For now, we'll return an empty list
    return []

def setup_routes(app: Flask, rescan: bool = False) -> None:
    """
    Set up the Flask routes for the application.
    
    Args:
        app (Flask): The Flask application instance.
        rescan (bool, optional): Whether to force a rescan of installed applications. Defaults to False.
    """
    from reformatbackup.src.scan import scan_installed_apps
    from reformatbackup.src.backup import backup_app, get_backup_location
    from reformatbackup.src.restore import restore_backup, get_backup_versions
    
    @app.route('/')
    def index() -> str:
        """
        Render the main application page.
        
        Returns:
            str: The rendered HTML template.
        """
        try:
            # Get the list of installed applications
            apps = scan_installed_apps(force_rescan=rescan)
            
            # Get the backup location
            backup_location = get_backup_location()
            
            # Calculate drive sizes
            drive_sizes = calculate_drive_sizes(apps)
            
            # Get recent backups (if any)
            recent_backups = get_recent_backups(limit=5)
            
            return render_template('index.html',
                                  apps=apps,
                                  backup_location=backup_location,
                                  drive_sizes=drive_sizes,
                                  recent_backups=recent_backups,
                                  update_available=app.config.get('UPDATE_AVAILABLE', False))
        except Exception as e:
            logger.error(f"Error rendering index page: {e}")
            return render_template('error.html',
                                  error_code=500,
                                  error_message=f"Error loading application data: {str(e)}"), 500
    
    @app.route('/backup', methods=['POST'])
    def backup() -> Any:
        """
        Handle backup requests.
        
        Returns:
            Any: JSON response or redirect.
        """
        if request.method == 'POST':
            app_ids = request.form.getlist('app_ids')
            
            if not app_ids:
                return jsonify({'error': 'No applications selected for backup'}), 400
            
            results = []
            for app_id in app_ids:
                result = backup_app(app_id)
                results.append(result)
            
            return jsonify({'results': results})
    
    @app.route('/restore/<app_id>')
    def restore_view(app_id: str) -> str:
        """
        Render the restore page for a specific application.
        
        Args:
            app_id (str): The ID of the application to restore.
            
        Returns:
            str: The rendered HTML template.
        """
        # Get the list of backup versions for the application
        versions = get_backup_versions(app_id)
        
        return render_template('restore.html', 
                              app_id=app_id, 
                              versions=versions)
    
    @app.route('/restore/<app_id>/<backup_id>', methods=['POST'])
    def restore_action(app_id: str, backup_id: str) -> Any:
        """
        Handle restore requests.
        
        Args:
            app_id (str): The ID of the application to restore.
            backup_id (str): The ID of the backup to restore.
            
        Returns:
            Any: JSON response or redirect.
        """
        if request.method == 'POST':
            backup_first = request.form.get('backup_first', 'false') == 'true'
            
            result = restore_backup(app_id, backup_id, backup_first=backup_first)
            
            return jsonify({'result': result})
    
    @app.route('/settings')
    def settings() -> str:
        """
        Render the settings page.
        
        Returns:
            str: The rendered HTML template.
        """
        try:
            # Get the backup location
            backup_location = get_backup_location()
            
            return render_template('settings.html',
                                  backup_location=backup_location,
                                  update_available=app.config.get('UPDATE_AVAILABLE', False))
        except Exception as e:
            logger.error(f"Error rendering settings page: {e}")
            return render_template('error.html',
                                  error_code=500,
                                  error_message=f"Error loading settings: {str(e)}"), 500
    
    @app.route('/settings/update-check', methods=['GET'])
    def get_update_check_settings() -> Any:
        """
        Get the update check settings.
        
        Returns:
            Any: JSON response with update check settings.
        """
        enabled = get_check_updates()
        return jsonify({"enabled": enabled})
    
    @app.route('/settings/update-check', methods=['POST'])
    def update_check_settings() -> Any:
        """
        Update the update check settings.
        
        Returns:
            Any: JSON response with success status.
        """
        try:
            data = request.json
            enabled = data.get('enabled', True)
            
            # Update the setting
            success = set_check_updates(enabled)
            
            return jsonify({"success": success})
        except Exception as e:
            logger.error(f"Error updating update check settings: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/settings', methods=['POST'])
    def update_settings() -> Any:
        """
        Handle settings update requests.
        
        Returns:
            Any: Redirect to the settings page.
        """
        if request.method == 'POST':
            try:
                backup_location = request.form.get('backup_location')
                
                if not backup_location:
                    logger.error("No backup location provided")
                    return render_template('error.html',
                                          error_code=400,
                                          error_message="No backup location provided"), 400
                
                # Validate the backup location
                if not os.path.isdir(backup_location):
                    try:
                        os.makedirs(backup_location, exist_ok=True)
                        logger.info(f"Created backup directory: {backup_location}")
                    except Exception as e:
                        logger.error(f"Error creating backup directory: {e}")
                        return render_template('error.html',
                                              error_code=400,
                                              error_message=f"Invalid backup location: {str(e)}"), 400
                
                # Update the backup location
                from reformatbackup.src.backup import set_backup_location
                set_backup_location(backup_location)
                
                return redirect(url_for('settings'))
            except Exception as e:
                logger.error(f"Error updating settings: {e}")
                return render_template('error.html',
                                      error_code=500,
                                      error_message=f"Error updating settings: {str(e)}"), 500