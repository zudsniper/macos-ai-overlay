"""
Constants module for macOS Multi-Overlay.

This module defines constants used throughout the application.
"""

# Apple libraries
from Quartz import (
    kCGEventFlagMaskAlternate,
    kCGEventFlagMaskCommand,
    kCGEventFlagMaskControl,
    kCGEventFlagMaskShift,
)

# Application name
APP_NAME = "Multi-Overlay"

# Frame save name for window position/size
FRAME_SAVE_NAME = "MultiOverlayWindowFrame"

# Permission check exit code
PERMISSION_CHECK_EXIT = 1

# Window appearance
CORNER_RADIUS = 15.0
DRAG_AREA_HEIGHT = 30

# Status item context
STATUS_ITEM_CONTEXT = 1

# Launcher trigger mask (all modifier keys)
LAUNCHER_TRIGGER_MASK = (
    kCGEventFlagMaskShift |
    kCGEventFlagMaskControl |
    kCGEventFlagMaskAlternate |
    kCGEventFlagMaskCommand
)

# Default unified menu trigger (Option + Shift + Space)
UNIFIED_MENU_TRIGGER = {
    "flags": kCGEventFlagMaskAlternate | kCGEventFlagMaskShift,
    "key": 49  # Space key
}
