"""
Main application UI for macOS Multi-Overlay.

This module provides the main application UI, including the overlay window
and integration with the overlay manager, hotkey manager, and menu-bar.
"""

import os
import sys
from typing import Dict, Optional, Any

from AppKit import (
    NSApp,
    NSApplication,
    NSBackingStoreBuffered,
    NSBorderlessWindowMask,
    NSButton,
    NSColor,
    NSDate,
    NSEvent,
    NSFloatingWindowLevel,
    NSFont,
    NSImage,
    NSMakeRect,
    NSObject,
    NSResizableWindowMask,
    NSSize,
    NSSquareStatusItemLength,
    NSStatusBar,
    NSTextAlignmentCenter,
    NSTextField,
    NSView,
    NSViewHeightSizable,
    NSViewWidthSizable,
    NSWindow,
    NSWindowCollectionBehaviorCanJoinAllSpaces,
    NSWindowCollectionBehaviorStationary,
    NSWindowDidResizeNotification,
    NSNotificationCenter,
    NSURL,
    NSURLRequest,
)
from WebKit import (
    WKWebView,
    WKWebViewConfiguration,
    WKUserScript,
    WKWebsiteDataStore,
)
from Quartz import (
    CGEventTapCreate,
    CGEventTapEnable,
    CFMachPortCreateRunLoopSource,
    CFRunLoopAddSource,
    CFRunLoopGetCurrent,
    CFRunLoopRun,
    kCGEventKeyDown,
    kCGEventMaskBit,
    kCGHeadInsertEventTap,
    kCGSessionEventTap,
    kCGEventTapOptionDefault,
    kCFRunLoopCommonModes,
)

from ..overlays import overlay_manager
from ..config.hotkeys import hotkey_manager
from ..constants import (
    APP_NAME,
    CORNER_RADIUS,
    DRAG_AREA_HEIGHT,
    FRAME_SAVE_NAME,
)
from ..launcher import (
    install_startup,
    uninstall_startup,
)
from .listener import (
    global_hotkey_listener,
    set_new_hotkey,
)
from .launcher import LaunchMenu
from .menu import MenuBarManager


# Custom window (contains entire application).
class AppWindow(NSWindow):
    """Custom window for the overlay application.
    
    This class provides a custom window implementation for the overlay
    application, with support for key window status and key events.
    """
    
    # Explicitly allow key window status
    def canBecomeKeyWindow(self):
        return True

    # Required to capture "Command+..." sequences.
    def keyDown_(self, event):
        self.delegate().keyDown_(event)


# Custom view (contains click-and-drag area on top sliver of overlay).
class DragArea(NSView):
    """Custom view for the drag area of the overlay window.
    
    This class provides a custom view implementation for the drag area
    of the overlay window, with support for background color and mouse
    events.
    """
    
    def initWithFrame_(self, frame):
        """Initialize the drag area with a frame.
        
        Args:
            frame: The frame for the drag area.
            
        Returns:
            The initialized drag area.
        """
        super(DragArea, self).initWithFrame_(frame)
        self.setWantsLayer_(True)
        return self
    
    # Used to update top-bar background to (roughly) match app color.
    def setBackgroundColor_(self, color):
        """Set the background color of the drag area.
        
        Args:
            color: The color to set.
        """
        self.layer().setBackgroundColor_(color.CGColor())

    # Used to capture the click-and-drag event.
    def mouseDown_(self, event):
        """Handle mouse down events.
        
        Args:
            event: The mouse event.
        """
        self.window().performWindowDragWithEvent_(event)


# The main delegate for running the overlay app.
class AppDelegate(NSObject):
    """Main delegate for the overlay application.
    
    This class provides the main delegate for the overlay application,
    handling window creation, overlay switching, hotkeys, and menu
    integration.
    """
    
    # The main application setup.
    def applicationDidFinishLaunching_(self, notification):
        """Handle application launch.
        
        Args:
            notification: The notification object.
        """
        # Run as accessory app
        NSApp.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        
        # Create a borderless, floating, resizable window
        self.window = AppWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(500, 200, 550, 580),
            NSBorderlessWindowMask | NSResizableWindowMask,
            NSBackingStoreBuffered,
            False
        )
        self.window.setLevel_(NSFloatingWindowLevel)
        self.window.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces
            | NSWindowCollectionBehaviorStationary
        )
        
        # Save the last position and size
        self.window.setFrameAutosaveName_(FRAME_SAVE_NAME)
        
        # Create the webview for the main application.
        config = WKWebViewConfiguration.alloc().init()
        config.preferences().setJavaScriptCanOpenWindowsAutomatically_(True)
        
        # Initialize the WebView with a frame
        self.webview = WKWebView.alloc().initWithFrame_configuration_(
            ((0, 0), (800, 600)),  # Frame: origin (0,0), size (800x600)
            config
        )
        self.webview.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)  # Resizes with window
        
        # Set a custom user agent
        safari_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
        self.webview.setCustomUserAgent_(safari_user_agent)
        
        # Make window transparent so that the corners can be rounded
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.clearColor())
        
        # Set up content view with rounded corners
        content_view = NSView.alloc().initWithFrame_(self.window.contentView().bounds())
        content_view.setWantsLayer_(True)
        content_view.layer().setCornerRadius_(CORNER_RADIUS)
        content_view.layer().setBackgroundColor_(NSColor.whiteColor().CGColor())
        self.window.setContentView_(content_view)
        
        # Set up drag area (top sliver, full width)
        content_bounds = content_view.bounds()
        self.drag_area = DragArea.alloc().initWithFrame_(
            NSMakeRect(0, content_bounds.size.height - DRAG_AREA_HEIGHT, content_bounds.size.width, DRAG_AREA_HEIGHT)
        )
        content_view.addSubview_(self.drag_area)
        
        # Add close button to the drag area
        close_button = NSButton.alloc().initWithFrame_(NSMakeRect(5, 5, 20, 20))
        close_button.setBordered_(False)
        close_button.setImage_(NSImage.imageWithSystemSymbolName_accessibilityDescription_("xmark.circle.fill", None))
        close_button.setTarget_(self)
        close_button.setAction_("hideWindow:")
        self.drag_area.addSubview_(close_button)
        
        # Update the webview sizing and insert it below drag area.
        content_view.addSubview_(self.webview)
        self.webview.setFrame_(NSMakeRect(0, 0, content_bounds.size.width, content_bounds.size.height - DRAG_AREA_HEIGHT))
        
        # Set up script message handler for background color changes
        configuration = self.webview.configuration()
        user_content_controller = configuration.userContentController()
        user_content_controller.addScriptMessageHandler_name_(self, "backgroundColorHandler")
        
        # Inject JavaScript to monitor background color changes
        script = """
            function sendBackgroundColor() {
                var bgColor = window.getComputedStyle(document.body).backgroundColor;
                window.webkit.messageHandlers.backgroundColorHandler.postMessage(bgColor);
            }
            window.addEventListener('load', sendBackgroundColor);
            new MutationObserver(sendBackgroundColor).observe(document.body, { attributes: true, attributeFilter: ['style'] });
        """
        user_script = WKUserScript.alloc().initWithSource_injectionTime_forMainFrameOnly_(script, WKUserScriptInjectionTimeAtDocumentEnd, True)
        user_content_controller.addUserScript_(user_script)
        
        # Create the menu-bar manager
        self.menu_manager = MenuBarManager(self)
        self.menu_manager.setup_menu()
        
        # Create the launch menu
        self.launch_menu = LaunchMenu(self.handle_overlay_selection)
        
        # Add resize observer
        NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
            self, 'windowDidResize:', NSWindowDidResizeNotification, self.window
        )
        
        # Add local mouse event monitor for left mouse down
        self.local_mouse_monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(
            NSEventMaskLeftMouseDown,  # Monitor left mouse-down events
            self.handleLocalMouseEvent  # Handler method
        )
        
        # Create the event tap for key-down events
        tap = CGEventTapCreate(
            kCGSessionEventTap,  # Tap at the session level
            kCGHeadInsertEventTap,  # Insert at the head of the event queue
            kCGEventTapOptionDefault,  # Actively filter events
            CGEventMaskBit(kCGEventKeyDown),  # Capture key-down events
            global_hotkey_listener(self),  # Your callback function
            None  # Optional user info (refcon)
        )
        
        if tap:
            # Integrate the tap into the run loop
            source = CFMachPortCreateRunLoopSource(None, tap, 0)
            CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopCommonModes)
            CGEventTapEnable(tap, True)
            CFRunLoopRun()  # Start the run loop
        else:
            print("Failed to create event tap. Check Accessibility permissions.")
        
        # Set the delegate of the window to this parent application.
        self.window.setDelegate_(self)
        
        # Load the current overlay
        self.load_current_overlay()
        
        # Make sure this window is shown and focused.
        self.showWindow_(None)
    
    def load_current_overlay(self) -> None:
        """Load the current overlay in the webview."""
        overlay = overlay_manager.get_current_overlay()
        if overlay:
            url = NSURL.URLWithString_(overlay.url)
            request = NSURLRequest.requestWithURL_(url)
            self.webview.loadRequest_(request)
    
    def handle_overlay_selection(self, overlay_id: str) -> None:
        """Handle overlay selection from the launch menu.
        
        Args:
            overlay_id: The ID of the selected overlay.
        """
        if overlay_manager.set_current_overlay(overlay_id):
            self.load_current_overlay()
            self.showWindow_(None)
    
    def toggle_overlay(self, overlay_id: str) -> None:
        """Toggle an overlay.
        
        Args:
            overlay_id: The ID of the overlay to toggle.
        """
        current_overlay = overlay_manager.get_current_overlay()
        
        # If the window is key and the current overlay is the requested one, hide it
        if self.window.isKeyWindow() and current_overlay and current_overlay.id == overlay_id:
            self.hideWindow_(None)
        else:
            # Otherwise, set the current overlay and show the window
            if overlay_manager.set_current_overlay(overlay_id):
                self.load_current_overlay()
                self.showWindow_(None)
    
    def show_launch_menu(self) -> None:
        """Show the unified launch menu."""
        self.launch_menu.show_at_cursor()
    
    # Logic to show the overlay, make it the key window, and focus on the typing area.
    def showWindow_(self, sender):
        """Show the overlay window.
        
        Args:
            sender: The sender of the action.
        """
        self.window.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)
        
        # Execute the JavaScript to focus the textarea in the WKWebView
        self.webview.evaluateJavaScript_completionHandler_(
            "document.querySelector('textarea').focus();", None
        )

    # Hide the overlay and allow focus to return to the next visible application.
    def hideWindow_(self, sender):
        """Hide the overlay window.
        
        Args:
            sender: The sender of the action.
        """
        NSApp.hide_(None)
    
    # Launch an overlay from the menu
    def launchOverlay_(self, sender):
        """Launch an overlay from the menu.
        
        Args:
            sender: The sender of the action.
        """
        overlay_id = sender.representedObject()
        if overlay_id:
            self.handle_overlay_selection(overlay_id)
    
    # Show the unified launch menu
    def showLaunchMenu_(self, sender):
        """Show the unified launch menu.
        
        Args:
            sender: The sender of the action.
        """
        self.show_launch_menu()
    
    # Set the unified menu hotkey
    def setUnifiedMenuHotkey_(self, sender):
        """Set the unified menu hotkey.
        
        Args:
            sender: The sender of the action.
        """
        set_new_hotkey(self, is_unified_menu=True)
    
    # Set the hotkey for an overlay
    def setOverlayHotkey_(self, sender):
        """Set the hotkey for an overlay.
        
        Args:
            sender: The sender of the action.
        """
        overlay_id = sender.representedObject()
        if overlay_id:
            set_new_hotkey(self, overlay_id=overlay_id)
    
    # Go to the default landing website for the current overlay
    def goToWebsite_(self, sender):
        """Go to the default landing website for the current overlay.
        
        Args:
            sender: The sender of the action.
        """
        self.load_current_overlay()
    
    # Clear the webview cache data (in case cookies cause errors).
    def clearWebViewData_(self, sender):
        """Clear the webview cache data.
        
        Args:
            sender: The sender of the action.
        """
        dataStore = self.webview.configuration().websiteDataStore()
        dataTypes = WKWebsiteDataStore.allWebsiteDataTypes()
        dataStore.removeDataOfTypes_modifiedSince_completionHandler_(
            dataTypes,
            NSDate.distantPast(),
            lambda: print("Data cleared")
        )

    # Install the app to run at login
    def install_(self, sender):
        """Install the app to run at login.
        
        Args:
            sender: The sender of the action.
        """
        if install_startup():
            # Exit the current process since a new one will launch.
            print("Installation successful, exiting.", flush=True)
            NSApp.terminate_(None)
        else:
            print("Installation unsuccessful.", flush=True)

    # Uninstall the app from running at login
    def uninstall_(self, sender):
        """Uninstall the app from running at login.
        
        Args:
            sender: The sender of the action.
        """
        if uninstall_startup():
            NSApp.hide_(None)

    # For capturing key commands while the key window (in focus).
    def keyDown_(self, event):
        """Handle key down events.
        
        Args:
            event: The key event.
        """
        modifiers = event.modifierFlags()
        key_command = modifiers & NSCommandKeyMask
        key_alt = modifiers & NSAlternateKeyMask
        key_shift = modifiers & NSShiftKeyMask
        key_control = modifiers & NSControlKeyMask
        key = event.charactersIgnoringModifiers()
        
        # Command (NOT alt)
        if (key_command or key_control) and (not key_alt):
            # Select all
            if key == 'a':
                self.window.firstResponder().selectAll_(None)
            # Copy
            elif key == 'c':
                self.window.firstResponder().copy_(None)
            # Cut
            elif key == 'x':
                self.window.firstResponder().cut_(None)
            # Paste
            elif key == 'v':
                self.window.firstResponder().paste_(None)
            # Hide
            elif key == 'h':
                self.hideWindow_(None)
            # Quit
            elif key == 'q':
                NSApp.terminate_(None)

    # Handler for capturing a click-and-drag event when not already the key window.
    def handleLocalMouseEvent(self, event):
        """Handle local mouse events.
        
        Args:
            event: The mouse event.
            
        Returns:
            The event to pass along, or None to consume the event.
        """
        if event.window() == self.window:
            # Get the click location in window coordinates
            click_location = event.locationInWindow()
            
            # Use hitTest_ to determine which view receives the click
            hit_view = self.window.contentView().hitTest_(click_location)
            
            # Check if the hit view is the drag area
            if hit_view == self.drag_area:
                # Bring the window to the front and make it key
                self.showWindow_(None)
                
                # Initiate window dragging with the event
                self.window.performWindowDragWithEvent_(event)
                return None  # Consume the event
        
        return event  # Pass unhandled events along

    # Handler for when the window resizes (adjusts the drag area).
    def windowDidResize_(self, notification):
        """Handle window resize events.
        
        Args:
            notification: The notification object.
        """
        bounds = self.window.contentView().bounds()
        w, h = bounds.size.width, bounds.size.height
        self.drag_area.setFrame_(NSMakeRect(0, h - DRAG_AREA_HEIGHT, w, DRAG_AREA_HEIGHT))
        self.webview.setFrame_(NSMakeRect(0, 0, w, h - DRAG_AREA_HEIGHT))

    # Handler for setting the background color based on the web page background color.
    def userContentController_didReceiveScriptMessage_(self, userContentController, message):
        """Handle script messages from the webview.
        
        Args:
            userContentController: The user content controller.
            message: The message object.
        """
        if message.name() == "backgroundColorHandler":
            bg_color_str = message.body()
            
            # Convert CSS color to NSColor (assuming RGB for simplicity)
            if bg_color_str.startswith("rgb") and ("(" in bg_color_str) and (")" in bg_color_str):
                rgb_values = [float(val) for val in bg_color_str[bg_color_str.index("(")+1:bg_color_str.index(")")].split(",")]
                r, g, b = [val / 255.0 for val in rgb_values[:3]]
                color = NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, 1.0)
                self.drag_area.setBackgroundColor_(color)
