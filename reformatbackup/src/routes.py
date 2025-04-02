"""
ReformatBackup - Routes

This module defines the Flask routes for the ReformatBackup application.
"""

import os
import logging
from typing import Any, Dict, List, Optional

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, current_app, session

from reformatbackup.src.config import (
    get_check_updates,
    set_check_updates,
    get_backup_location,
    get_compression_level,
    set_compression_level,
    get_backup_dot_files,
    set_backup_dot_files
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
    from reformatbackup.src.backup import backup_app, add_notes, get_recent_backups
    from reformatbackup.src.restore import restore_backup, get_backup_versions, get_backup_details
    
    @app.route('/')
    def index() -> str:
        """
        Render the main application page.
        
        Returns:
            str: The rendered HTML template.
        """
        try:
            # Check if rescan is requested
            force_rescan = request.args.get('rescan', 'false').lower() == 'true'
            # Get the list of installed applications
            apps = scan_installed_apps(force_rescan=force_rescan or rescan)
            
            # Get the backup location
            backup_location = get_backup_location()
            
            # Calculate drive sizes
            drive_sizes = calculate_drive_sizes(apps)
            
            # Get recent backups (if any)
            recent_backups = get_recent_backups(limit=5)
            
            # Group apps by source for statistics
            app_sources = {}
            for app in apps:
                source = app.get('source', 'unknown')
                if source in app_sources:
                    app_sources[source] += 1
                else:
                    app_sources[source] = 1
            
            # Sort apps by name by default
            apps = sorted(apps, key=lambda x: x.get('name', '').lower())
            
            return render_template('index.html',
                                  apps=apps,
                                  backup_location=backup_location,
                                  drive_sizes=drive_sizes,
                                  recent_backups=recent_backups,
                                  app_sources=app_sources,
                                  update_available=app.config.get('UPDATE_AVAILABLE', False))
        except Exception as e:
            logger.error(f"Error rendering index page: {e}")
            return render_template('error.html',
                                  error_code=500,
                                  error_message=f"Error loading application data: {str(e)}"), 500
    
    @app.route('/backup', methods=['GET', 'POST'])
    def backup() -> Any:
        """
        Handle backup requests and display the backup page.
        
        Returns:
            Any: JSON response, rendered template, or redirect.
        """
        # Get the backup location
        backup_location = get_backup_location()
        
        if request.method == 'POST':
            app_ids = request.form.getlist('app_ids')
            
            if not app_ids:
                return jsonify({'error': 'No applications selected for backup'}), 400
            
            # Get backup options from form
            compression_level = int(request.form.get('compression_level', get_compression_level()))
            backup_dot_files = request.form.get('backup_dot_files', '') == 'on'
            notes = request.form.get('notes', '')
            
            # Update configuration if needed
            if compression_level != get_compression_level():
                set_compression_level(compression_level)
            
            if backup_dot_files != get_backup_dot_files():
                set_backup_dot_files(backup_dot_files)
            
            # Perform backups
            results = []
            for app_id in app_ids:
                # Pass options to backup_app
                result = backup_app(app_id)
                
                # Add notes if provided and backup was successful
                if notes and result.get('success', False):
                    backup_id = f"{app_id}-{result.get('timestamp', '')}"
                    add_notes(backup_id, notes)
                
                results.append(result)
            
            return jsonify({'results': results})
        else:
            # GET request - display backup page
            # Check if we have app_ids in the query string or session
            app_ids = request.args.getlist('app_ids') or session.get('selected_app_ids', [])
            
            if not app_ids:
                # No apps selected, redirect to index
                return redirect(url_for('index'))
            
            # Store selected app_ids in session
            session['selected_app_ids'] = app_ids
            
            # Get app details for the selected apps
            apps = scan_installed_apps()
            selected_apps = [app for app in apps if app.get('id') in app_ids]
            
            # Get previous backups
            previous_backups = get_recent_backups(limit=10)
            
            return render_template('backup.html',
                                  backup_location=backup_location,
                                  compression_level=get_compression_level(),
                                  backup_dot_files=get_backup_dot_files(),
                                  selected_apps=selected_apps,
                                  previous_backups=previous_backups)
    
    @app.route('/backup/notes', methods=['POST'])
    def update_backup_notes() -> Any:
        """
        Update notes for a backup.
        
        Returns:
            Any: JSON response with success status.
        """
        try:
            data = request.json
            backup_id = data.get('backup_id')
            notes = data.get('notes', '')
            
            if not backup_id:
                return jsonify({'success': False, 'error': 'No backup ID provided'}), 400
            
            # Update the notes
            success = add_notes(backup_id, notes)
            
            return jsonify({'success': success})
        except Exception as e:
            logger.error(f"Error updating backup notes: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/restore/<app_id>')
    def restore_view(app_id: str) -> str:
        """
        Render the restore page for a specific application.
        
        Args:
            app_id (str): The ID of the application to restore.
            
        Returns:
            str: The rendered HTML template.
        """
        try:
            # Get the list of installed applications
            apps = scan_installed_apps()
            
            # Find the application
            app = None
            for a in apps:
                if a.get('id') == app_id:
                    app = a
                    break
            
            if not app:
                flash(f"Application with ID {app_id} not found", "danger")
                return redirect(url_for('index'))
            
            # Get the list of backup versions for the application
            versions = get_backup_versions(app_id)
            
            return render_template('restore.html',
                                app_id=app_id,
                                app_name=app.get('name', 'Unknown'),
                                app_path=app.get('path', 'Unknown'),
                                app_size=app.get('size', 0),
                                app_source=app.get('source', 'unknown'),
                                app_publisher=app.get('publisher', ''),
                                app_version=app.get('version', ''),
                                versions=versions,
                                backup_first_checked=True)
        except Exception as e:
            logger.error(f"Error rendering restore page: {e}")
            flash(f"Error loading restore page: {str(e)}", "danger")
            return redirect(url_for('index'))
    
    @app.route('/restore/details/<backup_id>')
    def backup_details(backup_id: str) -> Any:
        """
        Get details for a specific backup.
        
        Args:
            backup_id (str): The ID of the backup to get details for.
            
        Returns:
            Any: JSON response with backup details.
        """
        try:
            details = get_backup_details(backup_id)
            return jsonify(details)
        except Exception as e:
            logger.error(f"Error getting backup details: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
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
            try:
                # Get restore options from form
                backup_first = request.form.get('backup_first', 'false') == 'true'
                restore_dot_files = request.form.get('restore_dot_files', 'false') == 'true'
                conflict_resolution = request.form.get('conflict_resolution', 'overwrite-all')
                
                # Perform the restore
                result = restore_backup(
                    app_id,
                    backup_id,
                    backup_first=backup_first,
                    restore_dot_files=restore_dot_files,
                    conflict_resolution=conflict_resolution
                )
                
                return jsonify({'result': result})
            except Exception as e:
                logger.error(f"Error during restore: {e}")
                return jsonify({'result': {'success': False, 'error': str(e)}}), 500
    
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