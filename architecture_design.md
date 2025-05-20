# macOS Multi-Overlay Architecture Design

## Overview

The macOS Multi-Overlay project extends the existing macOS Grok overlay to support multiple AI assistant overlays with a plugin-friendly architecture. This document outlines the design for implementing multi-site support, plugin interfaces, trigger systems, and menu-bar integration.

## Core Components

### 1. Overlay Plugin System

#### Directory Structure
```
macos_multi_overlay/
├── overlays/                  # Directory for overlay definitions
│   ├── __init__.py            # Plugin discovery and registration
│   ├── base.py                # Base overlay class definition
│   ├── builtin/               # Built-in overlay implementations
│   │   ├── __init__.py
│   │   ├── grok.py            # Grok overlay implementation
│   │   ├── gemini.py          # Gemini overlay implementation
│   │   ├── claude.py          # Claude overlay implementation
│   │   └── chatgpt.py         # ChatGPT overlay implementation
│   └── custom/                # Directory for user-added overlays
├── config/                    # Configuration management
│   ├── __init__.py
│   ├── settings.py            # Global settings manager
│   └── hotkeys.py             # Hotkey configuration manager
└── ui/                        # UI components
    ├── __init__.py
    ├── app.py                 # Main application UI
    ├── menu.py                # Menu-bar implementation
    └── launcher.py            # Overlay launcher UI
```

#### Overlay Definition Format

Each overlay will be defined by a JSON or Python metadata file with the following structure:

**JSON Format** (for custom overlays):
```json
{
  "id": "unique_overlay_id",
  "name": "Display Name",
  "url": "https://example.com",
  "iconPath": "path/to/icon.png",
  "defaultHotkey": {
    "flags": 524288,  // Option key (kCGEventFlagMaskAlternate)
    "key": 49         // Space key
  },
  "description": "Optional description of the overlay"
}
```

**Python Format** (for built-in overlays):
```python
from macos_multi_overlay.overlays.base import Overlay

class ExampleOverlay(Overlay):
    id = "example"
    name = "Example Overlay"
    url = "https://example.com"
    icon_path = "path/to/icon.png"
    default_hotkey = {
        "flags": 524288,  # Option key (kCGEventFlagMaskAlternate)
        "key": 49         # Space key
    }
    description = "Optional description of the overlay"
```

### 2. Overlay Loader

The overlay loader will:
1. Discover and load all overlay definitions from both built-in and custom directories
2. Validate overlay metadata for required fields
3. Register overlays with the application
4. Provide methods to access overlay metadata by ID

```python
class OverlayManager:
    def __init__(self):
        self.overlays = {}  # Dictionary of overlay instances by ID
        
    def discover_overlays(self):
        # Load built-in overlays
        # Load custom JSON overlays
        # Register all valid overlays
        
    def get_overlay(self, overlay_id):
        # Return overlay instance by ID
        
    def get_all_overlays(self):
        # Return all registered overlays
```

### 3. Trigger System

#### Per-Overlay Hotkeys

Each overlay will have its own configurable global hotkey:

```python
class HotkeyManager:
    def __init__(self):
        self.hotkeys = {}  # Dictionary of hotkeys by overlay ID
        
    def load_hotkeys(self):
        # Load hotkey configurations from settings
        
    def save_hotkeys(self):
        # Save hotkey configurations to settings
        
    def register_hotkey(self, overlay_id, flags, key):
        # Register a hotkey for an overlay
        
    def handle_key_event(self, event, flags, keycode):
        # Check if the key event matches any registered hotkey
        # Return the overlay ID if matched, None otherwise
```

#### Unified Launch Menu

A single hotkey will trigger a contextual menu at the cursor position:

```python
class LaunchMenu:
    def __init__(self, overlay_manager):
        self.overlay_manager = overlay_manager
        
    def show_at_cursor(self):
        # Create a menu with all registered overlays
        # Show the menu at the current cursor position
        # Return the selected overlay ID
```

### 4. Menu-Bar Integration

The menu-bar will be refactored to support multiple overlays:

```python
class MenuBarManager:
    def __init__(self, overlay_manager):
        self.overlay_manager = overlay_manager
        self.status_item = None
        
    def setup_menu(self):
        # Create the status item
        # Create a dynamic menu with all registered overlays
        # Add settings and other menu items
```

## Application Flow

1. Application starts and initializes the OverlayManager
2. OverlayManager discovers and loads all overlays
3. HotkeyManager loads and registers hotkeys for each overlay
4. MenuBarManager creates the status item and menu
5. Global event listener is set up to handle hotkeys
6. When a hotkey is triggered, the corresponding overlay is shown/hidden
7. When the unified launch menu hotkey is triggered, the LaunchMenu is shown

## Configuration Management

Settings will be stored in JSON files:

```
~/Library/Application Support/macOS Multi-Overlay/
├── settings.json       # Global settings
├── hotkeys.json        # Hotkey configurations
└── overlays/           # Custom overlay definitions
```

## Command-Line Interface

The application will support the following command-line arguments:

```
--site SITE_ID          # Launch with a specific overlay
--list-sites            # List all available overlays
--install-startup       # Install the app to run at login
--uninstall-startup     # Uninstall the app from running at login
--check-permissions     # Check Accessibility permissions
```

## Implementation Strategy

1. Create the new directory structure
2. Implement the base Overlay class and OverlayManager
3. Create built-in overlay implementations
4. Refactor the main application to use the OverlayManager
5. Implement the HotkeyManager and LaunchMenu
6. Refactor the menu-bar implementation
7. Update documentation and add tests
