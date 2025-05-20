"""
Main module for macOS Multi-Overlay application.

This module provides the main entry point for the application and handles
command-line arguments, overlay selection, and application initialization.
"""

# Python libraries
import argparse
import sys
from typing import List, Optional

# Local libraries
from .overlays import overlay_manager
from .constants import APP_NAME
from .app import (
    AppDelegate,
    NSApplication
)
from .launcher import (
    check_permissions,
    ensure_accessibility_permissions,
    install_startup,
    uninstall_startup
)
from .health_checks import (
    health_check_decorator
)


# Main executable for running the application from the command line.
@health_check_decorator
def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description=f"macOS Multi-Overlay App - Dedicated window for AI assistants that can be summoned and dismissed with customizable keyboard shortcuts."
    )
    parser.add_argument(
        "--site",
        type=str,
        help="Specify which overlay to launch (e.g., grok, gemini, claude, chatgpt)",
    )
    parser.add_argument(
        "--list-sites",
        action="store_true",
        help="List all available overlay sites",
    )
    parser.add_argument(
        "--install-startup",
        action="store_true",
        help="Install the app to run at login",
    )
    parser.add_argument(
        "--uninstall-startup",
        action="store_true",
        help="Uninstall the app from running at login",
    )
    parser.add_argument(
        "--check-permissions",
        action="store_true",
        help="Check Accessibility permissions only"
    )
    args = parser.parse_args()

    # Discover available overlays
    overlay_manager.discover_overlays()
    
    # Handle --list-sites argument
    if args.list_sites:
        print("Available overlay sites:")
        for overlay in overlay_manager.get_all_overlays():
            print(f"  {overlay.id}: {overlay.name} - {overlay.description}")
        return

    # Handle --install-startup argument
    if args.install_startup:
        install_startup()
        return

    # Handle --uninstall-startup argument
    if args.uninstall_startup:
        uninstall_startup()
        return

    # Handle --check-permissions argument
    if args.check_permissions:
        is_trusted = check_permissions(ask=False)
        print("Permissions granted:", is_trusted)
        sys.exit(0 if is_trusted else 1)

    # Handle --site argument
    if args.site:
        if not overlay_manager.set_current_overlay(args.site):
            print(f"Error: Overlay '{args.site}' not found.")
            print("Available overlays:")
            for overlay in overlay_manager.get_all_overlays():
                print(f"  {overlay.id}: {overlay.name}")
            sys.exit(1)

    # Check permissions (make request to user) when launching, but proceed regardless.
    check_permissions()

    # Default behavior: run the app and inform user of startup options
    print()
    print(f"Starting macOS Multi-Overlay.")
    print()
    print(f"To run at login, use:      macos-multi-overlay --install-startup")
    print(f"To remove from login, use: macos-multi-overlay --uninstall-startup")
    print(f"To list available sites:   macos-multi-overlay --list-sites")
    print(f"To specify a site:         macos-multi-overlay --site SITE_ID")
    print()
    
    # Get the current overlay
    current_overlay = overlay_manager.get_current_overlay()
    if current_overlay:
        print(f"Launching overlay: {current_overlay.name} ({current_overlay.id})")
    else:
        print("Error: No overlay selected and no default overlay available.")
        sys.exit(1)
    
    # Initialize and run the application
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.run()


if __name__ == "__main__":
    # Execute the decorated main function.
    main()
