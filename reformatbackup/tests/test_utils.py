"""
Tests for the utility functions in the ReformatBackup application.
"""

import os
import json
import tempfile
import pytest
from datetime import datetime

from reformatbackup.src.utils import (
    format_size,
    format_timestamp,
    read_json,
    write_json,
    handle_hidden_files
)

class TestFormatSize:
    """Tests for the format_size function."""
    
    def test_format_bytes(self):
        """Test formatting bytes."""
        assert format_size(500) == "500 B"
    
    def test_format_kilobytes(self):
        """Test formatting kilobytes."""
        assert format_size(1500) == "1.46 KB"
    
    def test_format_megabytes(self):
        """Test formatting megabytes."""
        assert format_size(1500000) == "1.43 MB"
    
    def test_format_gigabytes(self):
        """Test formatting gigabytes."""
        assert format_size(1500000000) == "1.40 GB"

class TestFormatTimestamp:
    """Tests for the format_timestamp function."""
    
    def test_valid_timestamp(self):
        """Test formatting a valid timestamp."""
        assert format_timestamp("20240401-120000") == "2024-04-01 12:00:00"
    
    def test_invalid_timestamp(self):
        """Test formatting an invalid timestamp."""
        # Should return the original string if it can't be parsed
        assert format_timestamp("invalid") == "invalid"

class TestJsonFunctions:
    """Tests for the JSON reading and writing functions."""
    
    def test_write_and_read_json(self):
        """Test writing and reading a JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file path
            test_file = os.path.join(temp_dir, "test.json")
            
            # Test data
            test_data = {
                "name": "Test App",
                "version": "1.0.0",
                "settings": {
                    "theme": "dark",
                    "backup_location": "C:/backups"
                }
            }
            
            # Write the data
            result = write_json(test_file, test_data)
            assert result is True
            
            # Verify the file exists
            assert os.path.exists(test_file)
            
            # Read the data back
            read_data = read_json(test_file)
            
            # Verify the data matches
            assert read_data == test_data
    
    def test_read_nonexistent_json(self):
        """Test reading a JSON file that doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file path that doesn't exist
            test_file = os.path.join(temp_dir, "nonexistent.json")
            
            # Read the data
            read_data = read_json(test_file)
            
            # Should return an empty dictionary
            assert read_data == {}

class TestHiddenFiles:
    """Tests for the handle_hidden_files function."""
    
    def test_find_hidden_files(self):
        """Test finding hidden files in a directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some hidden files and directories
            hidden_dir = os.path.join(temp_dir, ".hidden_dir")
            os.makedirs(hidden_dir)
            
            hidden_file = os.path.join(temp_dir, ".hidden_file")
            with open(hidden_file, "w") as f:
                f.write("test")
            
            normal_file = os.path.join(temp_dir, "normal_file")
            with open(normal_file, "w") as f:
                f.write("test")
            
            # Find hidden files
            hidden_paths = handle_hidden_files(temp_dir)
            
            # Verify the hidden files and directories are found
            assert len(hidden_paths) == 2
            assert any(path.endswith(".hidden_dir") for path in hidden_paths)
            assert any(path.endswith(".hidden_file") for path in hidden_paths)