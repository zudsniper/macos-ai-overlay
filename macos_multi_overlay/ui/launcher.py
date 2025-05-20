"""
Launcher UI for macOS Multi-Overlay.

This module provides the unified launch menu for selecting overlays.
"""

import os
from typing import Callable, Optional

from AppKit import (
    NSApp,
    NSApplication,
    NSColor,
    NSEvent,
    NSFont,
    NSImage,
    NSMakeRect,
    NSMenu,
    NSMenuItem,
    NSPoint,
    NSScreen,
    NSSize,
    NSStatusBar,
    NSTextAlignmentCenter,
    NSTextField,
    NSView,
    NSWindow,
    NSWindowStyleMaskBorderless,
    NSBackingStoreBuffered,
    NSFloatingWindowLevel,
)

from ..overlays import overlay_manager


class LaunchMenu:
    """Unified launch menu for selecting overlays.
    
    This class provides a contextual menu at the cursor position for
    selecting overlays.
    """
    
    def __init__(self, callback: Callable[[str], None]):
        """Initialize the launch menu.
        
        Args:
            callback: Function to call when an overlay is selected.
                     The function should take the overlay ID as an argument.
        """
        self.callback = callback
        self.window = None
        
    def show_at_cursor(self) -> None:
        """Show the launch menu at the current cursor position."""
        # Get the current mouse location
        mouse_location = NSEvent.mouseLocation()
        
        # Create the menu
        menu = NSMenu.alloc().init()
        menu.setAutoenablesItems_(False)
        
        # Add menu items for each overlay
        for overlay in overlay_manager.get_all_overlays():
            # Create menu item
            item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                overlay.name, "selectOverlay:", ""
            )
            
            # Set the overlay ID as the represented object
            item.setRepresentedObject_(overlay.id)
            
            # Load the overlay icon if available
            if overlay.icon_path and os.path.exists(overlay.icon_path):
                icon = NSImage.alloc().initWithContentsOfFile_(overlay.icon_path)
                if icon:
                    icon.setSize_(NSSize(16, 16))
                    item.setImage_(icon)
            
            # Set the target to self
            item.setTarget_(self)
            
            # Add the item to the menu
            menu.addItem_(item)
        
        # Show the menu at the cursor position
        menu.popUpMenuPositioningItem_atLocation_inView_(
            None, mouse_location, None
        )
    
    def selectOverlay_(self, sender) -> None:
        """Handle overlay selection from the menu.
        
        Args:
            sender: The menu item that was selected.
        """
        overlay_id = sender.representedObject()
        if overlay_id:
            self.callback(overlay_id)
