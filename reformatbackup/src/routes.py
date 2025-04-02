"""
ReformatBackup - Routes

This module defines the Flask routes for the ReformatBackup application.
"""

import os
import logging
from typing import Any

from flask import Flask, render_template, request, jsonify, redirect, url_for

# Set up logging
logger = logging.getLogger(__name__)

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
        # Get the list of installed applications
        apps = scan_installed_apps(force_rescan=rescan)
        
        # Get the backup location
        backup_location = get_backup_location()
        
        return render_template('index.html', 
                              apps=apps, 
                              backup_location=backup_location,
                              update_available=False)  # This will be set in the main.py file
    
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
        # Get the backup location
        backup_location = get_backup_location()
        
        return render_template('settings.html', 
                              backup_location=backup_location)
    
    @app.route('/settings', methods=['POST'])
    def update_settings() -> Any:
        """
        Handle settings update requests.
        
        Returns:
            Any: Redirect to the settings page.
        """
        if request.method == 'POST':
            backup_location = request.form.get('backup_location')
            
            # Update the backup location
            from reformatbackup.src.backup import set_backup_location
            set_backup_location(backup_location)
            
            return redirect(url_for('settings'))