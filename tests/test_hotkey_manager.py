"""
Tests for hotkey management and trigger features.

This module provides tests for the hotkey manager and trigger system.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

from macos_multi_overlay.config.hotkeys import HotkeyManager
from macos_multi_overlay.overlays.base import Overlay


class TestHotkeyManager(unittest.TestCase):
    """Test cases for hotkey management."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for test configuration
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name)
        
        # Create a test hotkey manager
        self.manager = HotkeyManager()
        
        # Override the config directory and file
        self.original_config_dir = self.manager.CONFIG_DIR
        self.original_hotkeys_file = self.manager.HOTKEYS_FILE
        self.manager.CONFIG_DIR = self.config_dir
        self.manager.HOTKEYS_FILE = self.config_dir / "hotkeys.json"
        
    def tearDown(self):
        """Clean up the test environment."""
        self.temp_dir.cleanup()
        
        # Restore original paths
        self.manager.CONFIG_DIR = self.original_config_dir
        self.manager.HOTKEYS_FILE = self.original_hotkeys_file
        
    def test_get_set_overlay_hotkey(self):
        """Test getting and setting overlay hotkeys."""
        # Set a hotkey
        self.manager.set_overlay_hotkey("test", 524288, 49)
        
        # Get the hotkey
        hotkey = self.manager.get_overlay_hotkey("test")
        self.assertIsNotNone(hotkey)
        self.assertEqual(hotkey["flags"], 524288)
        self.assertEqual(hotkey["key"], 49)
        
    def test_get_set_unified_menu_hotkey(self):
        """Test getting and setting the unified menu hotkey."""
        # Get the default hotkey
        default_hotkey = self.manager.get_unified_menu_hotkey()
        self.assertIsNotNone(default_hotkey)
        
        # Set a new hotkey
        self.manager.set_unified_menu_hotkey(786432, 36)
        
        # Get the new hotkey
        hotkey = self.manager.get_unified_menu_hotkey()
        self.assertEqual(hotkey["flags"], 786432)
        self.assertEqual(hotkey["key"], 36)
        
    def test_handle_key_event(self):
        """Test handling key events."""
        # Set up some test hotkeys
        self.manager.set_overlay_hotkey("test1", 524288, 49)  # Option+Space
        self.manager.set_overlay_hotkey("test2", 786432, 36)  # Option+Command+Return
        self.manager.set_unified_menu_hotkey(655360, 53)  # Option+Control+Escape
        
        # Test matching the first overlay hotkey
        result = self.manager.handle_key_event(None, 524288, 49)
        self.assertEqual(result, "test1")
        
        # Test matching the second overlay hotkey
        result = self.manager.handle_key_event(None, 786432, 36)
        self.assertEqual(result, "test2")
        
        # Test matching the unified menu hotkey
        result = self.manager.handle_key_event(None, 655360, 53)
        self.assertEqual(result, "unified_menu")
        
        # Test non-matching hotkey
        result = self.manager.handle_key_event(None, 524288, 36)
        self.assertIsNone(result)
        
    def test_save_load_hotkeys(self):
        """Test saving and loading hotkeys."""
        # Set some test hotkeys
        self.manager.set_overlay_hotkey("test1", 524288, 49)
        self.manager.set_overlay_hotkey("test2", 786432, 36)
        self.manager.set_unified_menu_hotkey(655360, 53)
        
        # Save the hotkeys
        self.manager.save_hotkeys()
        
        # Create a new manager to load the hotkeys
        new_manager = HotkeyManager()
        new_manager.CONFIG_DIR = self.config_dir
        new_manager.HOTKEYS_FILE = self.config_dir / "hotkeys.json"
        
        # Load the hotkeys
        new_manager.load_hotkeys()
        
        # Check if the hotkeys were loaded correctly
        self.assertEqual(new_manager.get_overlay_hotkey("test1")["flags"], 524288)
        self.assertEqual(new_manager.get_overlay_hotkey("test1")["key"], 49)
        self.assertEqual(new_manager.get_overlay_hotkey("test2")["flags"], 786432)
        self.assertEqual(new_manager.get_overlay_hotkey("test2")["key"], 36)
        self.assertEqual(new_manager.get_unified_menu_hotkey()["flags"], 655360)
        self.assertEqual(new_manager.get_unified_menu_hotkey()["key"], 53)


class TestIntegration(unittest.TestCase):
    """Integration tests for overlay and hotkey systems."""
    
    def test_overlay_from_json_with_hotkey(self):
        """Test creating an overlay from JSON with a hotkey."""
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
        
        # Create an overlay from the JSON data
        overlay = Overlay.from_json(json_data)
        
        # Check if the overlay was created correctly
        self.assertEqual(overlay.id, "json_test")
        self.assertEqual(overlay.name, "JSON Test")
        self.assertEqual(overlay.url, "https://example.com/json")
        self.assertEqual(overlay.icon_path, "json_icon.png")
        self.assertEqual(overlay.default_hotkey["flags"], 524288)
        self.assertEqual(overlay.default_hotkey["key"], 49)
        self.assertEqual(overlay.description, "Test JSON overlay")
        
        # Create a hotkey manager
        manager = HotkeyManager()
        
        # Initialize hotkeys for the overlay
        if overlay.id not in manager.hotkeys:
            manager.hotkeys[overlay.id] = overlay.default_hotkey
        
        # Check if the hotkey was initialized correctly
        self.assertEqual(manager.get_overlay_hotkey("json_test")["flags"], 524288)
        self.assertEqual(manager.get_overlay_hotkey("json_test")["key"], 49)


if __name__ == "__main__":
    unittest.main()
