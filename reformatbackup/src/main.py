#!/usr/bin/env python3
"""
ReformatBackup - Main Entry Point

This module serves as the entry point for the ReformatBackup application.
It handles launching the Flask web server, checking for updates, and opening
the browser to the application interface.
"""

import os
import sys
import webbrowser
from threading import Timer
import argparse
import logging
import subprocess
import tempfile
from typing import Optional, Dict, Any

from flask import Flask

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(os.path.expanduser("~"), "reformatbackup.log")
        ),
    ],
)
logger = logging.getLogger(__name__)

# Flask configuration
class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-reformatbackup')
    TEMPLATES_AUTO_RELOAD = True
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload size
    
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

def create_app(config_object: object = None) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        config_object (object, optional): Configuration object to use. Defaults to None.
        
    Returns:
        Flask: The configured Flask application.
    """
    # Create Flask app with correct template and static folders
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"),
                static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"))
    
    # Configure the app
    if config_object is None:
        if os.environ.get('FLASK_ENV') == 'production':
            app.config.from_object(ProductionConfig)
        else:
            app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(config_object)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

def register_error_handlers(app: Flask) -> None:
    """
    Register error handlers for the Flask application.
    
    Args:
        app (Flask): The Flask application.
    """
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html',
                              error_code=404,
                              error_message="Page not found"), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html',
                              error_code=500,
                              error_message="Internal server error"), 500

# Create the Flask app
app = create_app()
def check_for_updates() -> Dict[str, Any]:
    """
    Check if a newer version of the application is available on PyPI.
    
    Returns:
        Dict[str, Any]: A dictionary containing update information.
    """
    from reformatbackup.src.config import get_check_updates
    
    # Check if update checking is enabled
    if not get_check_updates():
        logger.info("Update checking is disabled")
        return {"available": False, "disabled": True}
    
    try:
        import requests
        import pkg_resources
        
        current_version = pkg_resources.get_distribution("reformatbackup").version
        response = requests.get("https://pypi.org/pypi/reformatbackup/json")
        latest_version = response.json()["info"]["version"]
        
        if latest_version > current_version:
            logger.info(f"Update available: {latest_version} (current: {current_version})")
            return {
                "available": True,
                "current_version": current_version,
                "latest_version": latest_version,
                "release_notes": response.json()["info"].get("summary", "")
            }
        else:
            logger.info(f"No updates available. Current version: {current_version}")
            return {"available": False, "current_version": current_version}
    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
        return {"available": False, "error": str(e)}

def perform_update() -> Dict[str, Any]:
    """
    Perform an update of the application.
    
    Returns:
        Dict[str, Any]: A dictionary containing the result of the update.
    """
    try:
        # Create a temporary script to run the update
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write("""
import subprocess
import sys
import time

def update_reformatbackup():
    print("Updating ReformatBackup...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "reformatbackup"])
        print("Update successful! Please restart ReformatBackup.")
        return True
    except Exception as e:
        print(f"Error updating ReformatBackup: {e}")
        return False

if __name__ == "__main__":
    result = update_reformatbackup()
    # Keep the window open for a few seconds so the user can see the result
    time.sleep(5)
    sys.exit(0 if result else 1)
""")
            update_script = f.name
        
        # Run the update script in a new process
        subprocess.Popen([sys.executable, update_script],
                         creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        
        return {"success": True, "message": "Update process started. The application will restart when the update is complete."}
    except Exception as e:
        logger.error(f"Error starting update process: {e}")
        return {"success": False, "error": str(e)}
        return False

def open_browser(port: int) -> None:
    """
    Open the default web browser to the application URL.
    
    Args:
        port (int): The port number the Flask server is running on.
    """
    webbrowser.open(f"http://localhost:{port}")

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="ReformatBackup")
    parser.add_argument(
        "--port", type=int, default=5000, help="Port to run the server on (default: 5000)"
    )
    parser.add_argument(
        "--no-browser", action="store_true", help="Don't open the browser automatically"
    )
    parser.add_argument(
        "--rescan", action="store_true", help="Force a rescan of installed applications"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Run in debug mode"
    )
    return parser.parse_args()

def main() -> None:
    """
    Main entry point for the application.
    """
    # Parse command-line arguments
    args = parse_arguments()
    
    # Set up Flask routes
    from reformatbackup.src.routes import setup_routes
    from flask import render_template
    setup_routes(app, rescan=args.rescan)
    
    # Check for updates
    update_info = check_for_updates()
    
    # Set update info in app config for templates to access
    app.config['UPDATE_INFO'] = update_info
    app.config['UPDATE_AVAILABLE'] = update_info.get('available', False)
    
    if update_info.get("available", False):
        logger.info(f"Update available: {update_info.get('latest_version')} (current: {update_info.get('current_version')})")
    
    # Create error template if it doesn't exist
    create_error_template_if_missing()
    
    # Open browser after a short delay
    if not args.no_browser:
        Timer(1.5, open_browser, [args.port]).start()
    
    try:
        # Run the Flask server
        app.run(
            host="127.0.0.1",
            port=args.port,
            debug=args.debug,
            use_reloader=args.debug,
        )
    except Exception as e:
        logger.error(f"Error starting Flask server: {e}")
        sys.exit(1)

@app.route('/update', methods=['POST'])
def update():
    """
    Handle update requests.
    
    Returns:
        Any: JSON response with update status.
    """
    from flask import jsonify
    
    result = perform_update()
    return jsonify(result)

def create_error_template_if_missing() -> None:
    """
    Create the error template if it doesn't exist.
    """
    error_template_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "templates",
        "error.html"
    )
    
    if not os.path.exists(error_template_path):
        try:
            with open(error_template_path, 'w') as f:
                f.write("""{% extends "base.html" %}

{% block title %}ReformatBackup - Error {{ error_code }}{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-12 text-center">
        <h1>Error {{ error_code }}</h1>
        <p class="lead">{{ error_message }}</p>
        <a href="{{ url_for('index') }}" class="btn btn-primary">Return to Home</a>
    </div>
</div>
{% endblock %}""")
            logger.info(f"Created error template at {error_template_path}")
        except Exception as e:
            logger.error(f"Error creating error template: {e}")

if __name__ == "__main__":
    main()