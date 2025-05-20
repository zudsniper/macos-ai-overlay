"""
Listener module for macOS Multi-Overlay.

This module provides functionality for listening to global keyboard events
and triggering overlay actions based on hotkeys.
"""

import json
import time
from pathlib import Path
from typing import Callable, Dict, Optional, Any

from AppKit import (
    NSAlternateKeyMask,
    NSCommandKeyMask,
    NSControlKeyMask,
    NSEvent,
    NSShiftKeyMask,
)
from Quartz import (
    CGEventCreateKeyboardEvent,
    CGEventGetFlags,
    CGEventGetIntegerValueField,
    CGEventKeyboardGetUnicodeString,
    CGEventTapCreate,
    CGEventTapEnable,
    CFMachPortCreateRunLoopSource,
    CFRunLoopAddSource,
    CFRunLoopGetCurrent,
    kCGEventKeyDown,
    kCGEventFlagMaskAlternate,
    kCGEventFlagMaskCommand,
    kCGEventFlagMaskControl,
    kCGEventFlagMaskShift,
    kCGHeadInsertEventTap,
    kCGKeyboardEventKeycode,
    kCGSessionEventTap,
    kCGEventTapOptionDefault,
    kCFRunLoopCommonModes,
)

from ..config.hotkeys import hotkey_manager
from ..overlays import overlay_manager
from ..constants import LAUNCHER_TRIGGER_MASK

# Special key names for display
SPECIAL_KEY_NAMES = {
    49: "Space", 36: "Return", 53: "Escape",
    122: "F1", 120: "F2", 99: "F3", 118: "F4",
    96: "F5", 97: "F6", 98: "F7", 100: "F8",
    101: "F9", 109: "F10", 103: "F11", 111: "F12",
    123: "Left Arrow", 124: "Right Arrow",
    125: "Down Arrow", 126: "Up Arrow"
}

# Global variable for new trigger handler
handle_new_trigger = None


# Helper function to get modifier names
def get_modifier_names(flags: int) -> list:
    """Get human-readable names for modifier flags.
    
    Args:
        flags: The modifier flags.
        
    Returns:
        A list of modifier names.
    """
    modifier_names = []
    if flags & NSShiftKeyMask:
        modifier_names.append("Shift")
    if flags & NSControlKeyMask:
        modifier_names.append("Control")
    if flags & NSAlternateKeyMask:
        modifier_names.append("Option")
    if flags & NSCommandKeyMask:
        modifier_names.append("Command")
    return modifier_names


# Get human-readable string for the trigger
def get_trigger_string(event, flags: int, keycode: int) -> str:
    """Get a human-readable string for a key combination.
    
    Args:
        event: The event object.
        flags: The modifier flags.
        keycode: The key code.
        
    Returns:
        A human-readable string for the key combination.
    """
    # Get the modifier names
    modifier_names = get_modifier_names(flags)
    
    # Get the key name
    if keycode in SPECIAL_KEY_NAMES:
        key_name = SPECIAL_KEY_NAMES[keycode]
    else:
        key_name = NSEvent.eventWithCGEvent_(event).characters()
    
    # Generate a plain text of the keys
    return " + ".join(modifier_names + [key_name]) if modifier_names else key_name


# Global event listener for handling hotkeys
def global_hotkey_listener(app):
    """Create a global event listener for handling hotkeys.
    
    Args:
        app: The application delegate.
        
    Returns:
        A function that handles key events.
    """
    def listener(proxy, event_type, event, refcon):
        if event_type == kCGEventKeyDown:
            keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
            flags = CGEventGetFlags(event) & LAUNCHER_TRIGGER_MASK
            
            # Handle setting a new trigger
            if handle_new_trigger:
                handle_new_trigger(event, flags, keycode)
                return None
            
            # Handle hotkeys
            result = hotkey_manager.handle_key_event(event, flags, keycode)
            
            if result == 'unified_menu':
                # Show the unified launch menu
                app.show_launch_menu()
                return None
            elif result:
                # Toggle the overlay
                app.toggle_overlay(result)
                return None
        
        return event
    
    return listener


# Function to set a new hotkey
def set_new_hotkey(app, overlay_id: Optional[str] = None, is_unified_menu: bool = False):
    """Set a new hotkey for an overlay or the unified menu.
    
    Args:
        app: The application delegate.
        overlay_id: The ID of the overlay to set a hotkey for, or None for the unified menu.
        is_unified_menu: Whether to set the unified menu hotkey.
    """
    global handle_new_trigger
    
    # Define the handler for the new trigger
    def custom_handle_new_trigger(event, flags, keycode):
        if is_unified_menu:
            hotkey_manager.set_unified_menu_hotkey(flags, keycode)
            trigger_str = get_trigger_string(event, flags, keycode)
            print(f"New unified menu trigger set: {trigger_str}")
        elif overlay_id:
            hotkey_manager.set_overlay_hotkey(overlay_id, flags, keycode)
            overlay = overlay_manager.get_overlay(overlay_id)
            trigger_str = get_trigger_string(event, flags, keycode)
            print(f"New hotkey for {overlay.name} set: {trigger_str}")
        
        # Reset the handler
        global handle_new_trigger
        handle_new_trigger = None
        
        return None
    
    # Set the global handler
    handle_new_trigger = custom_handle_new_trigger
