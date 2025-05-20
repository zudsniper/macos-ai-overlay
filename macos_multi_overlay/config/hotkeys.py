"""
Hotkey configuration manager for macOS Multi-Overlay.

This module provides functionality for managing per-overlay hotkeys and
the unified launch menu hotkey.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any

from ..overlays import overlay_manager
from ..constants import LAUNCHER_TRIGGER_MASK, UNIFIED_MENU_TRIGGER


# Directory for storing configuration files
CONFIG_DIR = Path.home() / "Library" / "Application Support" / "macOS Multi-Overlay"
# File for storing hotkey configurations
HOTKEYS_FILE = CONFIG_DIR / "hotkeys.json"


class HotkeyManager:
    """Manager for per-overlay hotkeys and unified launch menu hotkey.
    
    This class handles loading, saving, and managing hotkey configurations
    for overlays and the unified launch menu.
    """
    
    def __init__(self):
        """Initialize the hotkey manager."""
        self.hotkeys: Dict[str, Dict[str, Any]] = {}
        self.unified_menu_hotkey: Dict[str, Any] = UNIFIED_MENU_TRIGGER.copy()
        self.current_overlay_id: Optional[str] = None
        
        # Ensure the config directory exists
        os.makedirs(CONFIG_DIR, exist_ok=True)
        
        # Load hotkey configurations
        self.load_hotkeys()
    
    def load_hotkeys(self) -> None:
        """Load hotkey configurations from the settings file."""
        if HOTKEYS_FILE.exists():
            try:
                with open(HOTKEYS_FILE, 'r') as f:
                    data = json.load(f)
                
                # Load overlay hotkeys
                if 'overlays' in data:
                    self.hotkeys = data['overlays']
                
                # Load unified menu hotkey
                if 'unified_menu' in data:
                    self.unified_menu_hotkey = data['unified_menu']
            except Exception as e:
                print(f"Error loading hotkey configurations: {e}")
        
        # Initialize hotkeys for all overlays
        for overlay in overlay_manager.get_all_overlays():
            if overlay.id not in self.hotkeys:
                self.hotkeys[overlay.id] = overlay.default_hotkey
    
    def save_hotkeys(self) -> None:
        """Save hotkey configurations to the settings file."""
        data = {
            'overlays': self.hotkeys,
            'unified_menu': self.unified_menu_hotkey
        }
        
        try:
            with open(HOTKEYS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving hotkey configurations: {e}")
    
    def get_overlay_hotkey(self, overlay_id: str) -> Optional[Dict[str, Any]]:
        """Get the hotkey configuration for an overlay.
        
        Args:
            overlay_id: The ID of the overlay.
            
        Returns:
            The hotkey configuration for the overlay, or None if not found.
        """
        return self.hotkeys.get(overlay_id)
    
    def set_overlay_hotkey(self, overlay_id: str, flags: int, key: int) -> None:
        """Set the hotkey configuration for an overlay.
        
        Args:
            overlay_id: The ID of the overlay.
            flags: The modifier flags for the hotkey.
            key: The key code for the hotkey.
        """
        self.hotkeys[overlay_id] = {
            'flags': flags,
            'key': key
        }
        self.save_hotkeys()
    
    def get_unified_menu_hotkey(self) -> Dict[str, Any]:
        """Get the unified menu hotkey configuration.
        
        Returns:
            The unified menu hotkey configuration.
        """
        return self.unified_menu_hotkey
    
    def set_unified_menu_hotkey(self, flags: int, key: int) -> None:
        """Set the unified menu hotkey configuration.
        
        Args:
            flags: The modifier flags for the hotkey.
            key: The key code for the hotkey.
        """
        self.unified_menu_hotkey = {
            'flags': flags,
            'key': key
        }
        self.save_hotkeys()
    
    def handle_key_event(self, event, flags: int, keycode: int) -> Optional[str]:
        """Handle a key event and determine if it matches any hotkey.
        
        Args:
            event: The event object.
            flags: The modifier flags for the event.
            keycode: The key code for the event.
            
        Returns:
            The ID of the matched overlay, 'unified_menu' for the unified
            menu hotkey, or None if no match.
        """
        # Check if the event matches the unified menu hotkey
        if (flags == self.unified_menu_hotkey['flags'] and 
            keycode == self.unified_menu_hotkey['key']):
            return 'unified_menu'
        
        # Check if the event matches any overlay hotkey
        for overlay_id, hotkey in self.hotkeys.items():
            if (flags == hotkey['flags'] and keycode == hotkey['key']):
                return overlay_id
        
        return None


# Create a singleton instance of the hotkey manager
hotkey_manager = HotkeyManager()
