"""
Tests for overlay loading and management.

This module provides tests for the overlay loader and manager.
"""

import os
import json
import tempfile
import unittest
from pathlib import Path

from macos_multi_overlay.overlays.base import Overlay
from macos_multi_overlay.overlays import OverlayManager


class TestOverlay(Overlay):
    """Test overlay implementation for unit tests."""
    id = "test"
    name = "Test Overlay"
    url = "https://example.com"
    icon_path = "test_icon.png"
    default_hotkey = {
        "flags": 524288,
        "key": 49
    }
    description = "Test overlay for unit tests"


class TestOverlayLoader(unittest.TestCase):
    """Test cases for overlay loading and management."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for test overlays
        self.temp_dir = tempfile.TemporaryDirectory()
        self.custom_dir = Path(self.temp_dir.name) / "custom"
        self.custom_dir.mkdir(exist_ok=True)
        
        # Create a test manager
        self.manager = OverlayManager()
        
        # Override the custom directory path
        self.original_custom_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "overlays" / "custom"
        
    def tearDown(self):
        """Clean up the test environment."""
        self.temp_dir.cleanup()
        
    def test_register_overlay(self):
        """Test registering an overlay."""
        overlay = TestOverlay()
        self.manager.register_overlay(overlay)
        
        self.assertIn("test", self.manager.overlays)
        self.assertEqual(self.manager.get_overlay("test"), overlay)
        
    def test_get_all_overlays(self):
        """Test getting all registered overlays."""
        overlay1 = TestOverlay()
        overlay2 = TestOverlay()
        overlay2.id = "test2"
        
        self.manager.register_overlay(overlay1)
        self.manager.register_overlay(overlay2)
        
        overlays = self.manager.get_all_overlays()
        self.assertEqual(len(overlays), 2)
        self.assertIn(overlay1, overlays)
        self.assertIn(overlay2, overlays)
        
    def test_set_current_overlay(self):
        """Test setting the current overlay."""
        overlay = TestOverlay()
        self.manager.register_overlay(overlay)
        
        result = self.manager.set_current_overlay("test")
        self.assertTrue(result)
        self.assertEqual(self.manager.current_overlay_id, "test")
        
        # Test setting a non-existent overlay
        result = self.manager.set_current_overlay("nonexistent")
        self.assertFalse(result)
        self.assertEqual(self.manager.current_overlay_id, "test")  # Should not change
        
    def test_get_current_overlay(self):
        """Test getting the current overlay."""
        overlay = TestOverlay()
        self.manager.register_overlay(overlay)
        self.manager.set_current_overlay("test")
        
        current = self.manager.get_current_overlay()
        self.assertEqual(current, overlay)
        
    def test_json_overlay_loading(self):
        """Test loading an overlay from JSON."""
        # Create a test JSON overlay
        json_data = {
            "id": "json_test",
            "name": "JSON Test",
            "url": "https://example.com/json",
            "iconPath": "json_icon.png",
            "defaultHotkey": {
                "flags": 524288,
                "key": 49
            },
            "description": "Test JSON overlay"
        }
        
        json_path = self.custom_dir / "test_overlay.json"
        with open(json_path, "w") as f:
            json.dump(json_data, f)
        
        # Create a custom _discover_custom_overlays method for testing
        def mock_discover_custom_overlays(self):
            custom_dir = self.custom_dir
            
            # Process all JSON files in the custom directory
            for filename in os.listdir(custom_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(custom_dir, filename)
                    
                    try:
                        # Load the JSON file
                        with open(file_path, 'r') as f:
                            json_data = json.load(f)
                        
                        # Create an overlay from the JSON data
                        overlay = Overlay.from_json(json_data)
                        
                        # Register the overlay
                        if overlay.validate():
                            self.register_overlay(overlay)
                    except Exception as e:
                        print(f"Error loading custom overlay {filename}: {e}")
        
        # Replace the method temporarily
        original_method = self.manager._discover_custom_overlays
        self.manager._discover_custom_overlays = lambda: mock_discover_custom_overlays(self.manager)
        
        try:
            # Discover overlays
            self.manager._discover_custom_overlays()
            
            # Check if the JSON overlay was loaded
            overlay = self.manager.get_overlay("json_test")
            self.assertIsNotNone(overlay)
            self.assertEqual(overlay.name, "JSON Test")
            self.assertEqual(overlay.url, "https://example.com/json")
        finally:
            # Restore the original method
            self.manager._discover_custom_overlays = original_method


if __name__ == "__main__":
    unittest.main()
