"""
ReformatBackup - Utility Functions

This module provides utility functions for the ReformatBackup application.
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

def compress_to_7z(source: str, destination: str, compression_level: int = 9) -> bool:
    """
    Compress a file or directory to a 7z archive.
    
    Args:
        source (str): The path to the file or directory to compress.
        destination (str): The path to the 7z archive to create.
        compression_level (int, optional): The compression level (0-9). Defaults to 9.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        with py7zr.SevenZipFile(destination, mode="w", filters=[{"id": py7zr.FILTER_LZMA2, "preset": compression_level}]) as archive:
            if os.path.isdir(source):
                # Add directory contents
                for root, dirs, files in os.walk(source):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            # Calculate the archive path (relative to the source)
                            arcname = os.path.relpath(file_path, os.path.dirname(source))
                            archive.write(file_path, arcname)
                        except Exception as e:
                            logger.error(f"Error adding file to archive: {e}")
            else:
                # Add file
                try:
                    archive.write(source, os.path.basename(source))
                except Exception as e:
                    logger.error(f"Error adding file to archive: {e}")
        return True
    except Exception as e:
        logger.error(f"Error creating archive: {e}")
        return False

def extract_from_7z(source: str, destination: str) -> bool:
    """
    Extract a 7z archive to a directory.
    
    Args:
        source (str): The path to the 7z archive to extract.
        destination (str): The path to the directory to extract to.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Create the destination directory if it doesn't exist
        os.makedirs(destination, exist_ok=True)
        
        # Extract the archive
        with py7zr.SevenZipFile(source, mode="r") as archive:
            archive.extractall(destination)
        
        return True
    except Exception as e:
        logger.error(f"Error extracting archive: {e}")
        return False

def read_json(file_path: str) -> Dict[str, Any]:
    """
    Read a JSON file.
    
    Args:
        file_path (str): The path to the JSON file to read.
    
    Returns:
        Dict[str, Any]: The JSON data as a dictionary.
    """
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading JSON file: {e}")
        return {}

def write_json(file_path: str, data: Dict[str, Any]) -> bool:
    """
    Write a dictionary to a JSON file.
    
    Args:
        file_path (str): The path to the JSON file to write.
        data (Dict[str, Any]): The data to write.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write the data
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"Error writing JSON file: {e}")
        return False

def handle_hidden_files(path: str) -> List[str]:
    """
    Find hidden files and directories in a path.
    
    Args:
        path (str): The path to search for hidden files and directories.
    
    Returns:
        List[str]: A list of paths to hidden files and directories.
    """
    hidden_paths = []
    
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            # Add hidden directories
            for dir in dirs:
                if dir.startswith("."):
                    hidden_paths.append(os.path.join(root, dir))
            
            # Add hidden files
            for file in files:
                if file.startswith("."):
                    hidden_paths.append(os.path.join(root, file))
    elif os.path.isfile(path) and os.path.basename(path).startswith("."):
        hidden_paths.append(path)
    
    return hidden_paths

def format_size(size_bytes: int) -> str:
    """
    Format a size in bytes to a human-readable string.
    
    Args:
        size_bytes (int): The size in bytes.
    
    Returns:
        str: The formatted size string.
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def format_timestamp(timestamp: str) -> str:
    """
    Format a timestamp string to a human-readable string.
    
    Args:
        timestamp (str): The timestamp string in the format "YYYYMMDD-HHMMSS".
    
    Returns:
        str: The formatted timestamp string.
    """
    try:
        dt = datetime.datetime.strptime(timestamp, "%Y%m%d-%H%M%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logger.error(f"Error formatting timestamp: {e}")
        return timestamp