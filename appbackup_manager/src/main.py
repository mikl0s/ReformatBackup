#!/usr/bin/env python3
"""
AppBackup Manager - Main Entry Point

This module serves as the entry point for the AppBackup Manager application.
It handles launching the Flask web server, checking for updates, and opening
the browser to the application interface.
"""

import os
import sys
import webbrowser
from threading import Timer
import argparse
import logging
from typing import Optional

from flask import Flask

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(os.path.expanduser("~"), "appbackup.log")
        ),
    ],
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"),
            static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"))

def check_for_updates() -> bool:
    """
    Check if a newer version of the application is available on PyPI.
    
    Returns:
        bool: True if an update is available, False otherwise.
    """
    try:
        import requests
        import pkg_resources
        
        current_version = pkg_resources.get_distribution("appbackup-manager").version
        response = requests.get("https://pypi.org/pypi/appbackup-manager/json")
        latest_version = response.json()["info"]["version"]
        
        if latest_version > current_version:
            logger.info(f"Update available: {latest_version} (current: {current_version})")
            return True
        else:
            logger.info(f"No updates available. Current version: {current_version}")
            return False
    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
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
    parser = argparse.ArgumentParser(description="AppBackup Manager")
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
    from appbackup_manager.src.routes import setup_routes
    setup_routes(app, rescan=args.rescan)
    
    # Check for updates
    update_available = check_for_updates()
    if update_available:
        logger.info("Run 'pip install --upgrade appbackup-manager' to update")
    
    # Open browser after a short delay
    if not args.no_browser:
        Timer(1.5, open_browser, [args.port]).start()
    
    # Run the Flask server
    app.run(
        host="127.0.0.1",
        port=args.port,
        debug=args.debug,
        use_reloader=args.debug,
    )

if __name__ == "__main__":
    main()