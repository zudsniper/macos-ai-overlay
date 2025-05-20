"""
Menu module for macOS Multi-Overlay.

This module provides the menu-bar implementation for the application.
"""

import os
from typing import Callable, Dict, List, Optional

from AppKit import (
    NSApp,
    NSImage,
    NSMenu,
    NSMenuItem,
    NSSize,
    NSSquareStatusItemLength,
    NSStatusBar,
    NSKeyValueObservingOptionNew,
    NSAppearanceNameAqua,
    NSAppearanceNameDarkAqua,
)

from ..overlays import overlay_manager
from ..constants import STATUS_ITEM_CONTEXT


class MenuBarManager:
    """Manager for the menu-bar implementation.
    
    This class handles the creation and management of the menu-bar status
    item and menu.
    """
    
    def __init__(self, app_delegate):
        """Initialize the menu-bar manager.
        
        Args:
            app_delegate: The application delegate.
        """
        self.app_delegate = app_delegate
        self.status_item = None
        self.overlay_icons = {}  # Cache for overlay icons
        
    def setup_menu(self) -> None:
        """Set up the menu-bar status item and menu."""
        # Create status bar item
        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(NSSquareStatusItemLength)
        
        # Load default icon
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(os.path.dirname(script_dir))
        
        # Try to load white and black versions of the icon
        icon_white_path = os.path.join(base_dir, "images", "multi_overlay_white.png")
        icon_black_path = os.path.join(base_dir, "images", "multi_overlay_black.png")
        
        self.icon_white = None
        self.icon_black = None
        
        if os.path.exists(icon_white_path):
            self.icon_white = NSImage.alloc().initWithContentsOfFile_(icon_white_path)
            self.icon_white.setSize_(NSSize(18, 18))
            
        if os.path.exists(icon_black_path):
            self.icon_black = NSImage.alloc().initWithContentsOfFile_(icon_black_path)
            self.icon_black.setSize_(NSSize(18, 18))
        
        # Set the initial icon based on the current appearance
        self.update_status_item_image()
        
        # Observe system appearance changes
        self.status_item.button().addObserver_forKeyPath_options_context_(
            self, "effectiveAppearance", NSKeyValueObservingOptionNew, STATUS_ITEM_CONTEXT
        )
        
        # Create the menu
        self.update_menu()
    
    def update_menu(self) -> None:
        """Update the menu with the current overlays."""
        menu = NSMenu.alloc().init()
        
        # Create "Launch Overlay" submenu
        launch_menu = NSMenu.alloc().init()
        
        # Add items for each overlay
        for overlay in overlay_manager.get_all_overlays():
            # Create menu item
            item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                overlay.name, "launchOverlay:", ""
            )
            
            # Set the overlay ID as the represented object
            item.setRepresentedObject_(overlay.id)
            
            # Load the overlay icon if available
            if overlay.id in self.overlay_icons:
                icon = self.overlay_icons[overlay.id]
            elif overlay.icon_path and os.path.exists(overlay.icon_path):
                icon = NSImage.alloc().initWithContentsOfFile_(overlay.icon_path)
                if icon:
                    icon.setSize_(NSSize(16, 16))
                    self.overlay_icons[overlay.id] = icon
                else:
                    icon = None
            else:
                icon = None
                
            if icon:
                item.setImage_(icon)
            
            # Set tooltip with description if available
            if overlay.description:
                item.setToolTip_(overlay.description)
            
            # Set the target to the app delegate
            item.setTarget_(self.app_delegate)
            
            # Add the item to the launch menu
            launch_menu.addItem_(item)
        
        # Create the "Launch Overlay" menu item
        launch_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Launch Overlay", None, ""
        )
        launch_item.setSubmenu_(launch_menu)
        menu.addItem_(launch_item)
        
        # Add separator
        menu.addItem_(NSMenuItem.separatorItem())
        
        # Add "Show Unified Menu" item
        show_menu_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Show Overlay Selector", "showLaunchMenu:", ""
        )
        show_menu_item.setTarget_(self.app_delegate)
        menu.addItem_(show_menu_item)
        
        # Add "Set Unified Menu Hotkey" item
        set_menu_hotkey_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Set Overlay Selector Hotkey", "setUnifiedMenuHotkey:", ""
        )
        set_menu_hotkey_item.setTarget_(self.app_delegate)
        menu.addItem_(set_menu_hotkey_item)
        
        # Add separator
        menu.addItem_(NSMenuItem.separatorItem())
        
        # Add "Clear Web Cache" item
        clear_data_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Clear Web Cache", "clearWebViewData:", ""
        )
        clear_data_item.setTarget_(self.app_delegate)
        menu.addItem_(clear_data_item)
        
        # Add "Install Autolauncher" item
        install_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Install Autolauncher", "install:", ""
        )
        install_item.setTarget_(self.app_delegate)
        menu.addItem_(install_item)
        
        # Add "Uninstall Autolauncher" item
        uninstall_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Uninstall Autolauncher", "uninstall:", ""
        )
        uninstall_item.setTarget_(self.app_delegate)
        menu.addItem_(uninstall_item)
        
        # Add "Quit" item
        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Quit", "terminate:", "q"
        )
        quit_item.setTarget_(NSApp)
        menu.addItem_(quit_item)
        
        # Set the menu
        self.status_item.setMenu_(menu)
    
    def update_status_item_image(self) -> None:
        """Update the status item image based on the current appearance."""
        if not self.status_item or not self.status_item.button():
            return
            
        appearance = self.status_item.button().effectiveAppearance()
        
        if appearance.bestMatchFromAppearancesWithNames_([NSAppearanceNameAqua, NSAppearanceNameDarkAqua]) == NSAppearanceNameDarkAqua:
            if self.icon_white:
                self.status_item.button().setImage_(self.icon_white)
        else:
            if self.icon_black:
                self.status_item.button().setImage_(self.icon_black)
    
    def observeValueForKeyPath_ofObject_change_context_(self, keyPath, object, change, context):
        """Handle observation of appearance changes.
        
        Args:
            keyPath: The key path that changed.
            object: The object that changed.
            change: The change dictionary.
            context: The context.
        """
        if context == STATUS_ITEM_CONTEXT and keyPath == "effectiveAppearance":
            self.update_status_item_image()
