# Overlay Plugin API Documentation

This document describes how to create and add custom overlays to the macOS Multi-Overlay application.

## Overview

The macOS Multi-Overlay application supports a plugin-based architecture that allows you to add custom overlays for any web-based AI assistant or service. Overlays can be added in two ways:

1. **JSON Configuration Files**: Simple method for adding basic overlays without coding
2. **Python Classes**: Advanced method for overlays that need custom behavior

All overlay definitions must include certain required fields and can optionally include additional configuration.

## Directory Structure

Custom overlays are stored in the following location:

```
~/Library/Application Support/macOS Multi-Overlay/overlays/
```

This directory is automatically created when the application first runs. You can place your custom overlay definitions in this directory, and they will be discovered and loaded when the application starts.

## JSON Overlay Format

To create a custom overlay using JSON, create a file with a `.json` extension in the overlays directory. The file should contain a JSON object with the following structure:

```json
{
  "id": "unique_overlay_id",
  "name": "Display Name",
  "url": "https://example.com",
  "iconPath": "path/to/icon.png",
  "defaultHotkey": {
    "flags": 524288,
    "key": 49
  },
  "description": "Optional description of the overlay"
}
```

### Required Fields

- `id`: A unique identifier for the overlay (lowercase, no spaces)
- `name`: The display name shown in menus and UI
- `url`: The URL to load in the overlay window
- `iconPath`: Path to the overlay icon (can be absolute or relative to the JSON file)

### Optional Fields

- `defaultHotkey`: Default keyboard shortcut configuration
  - `flags`: Modifier key flags (see Modifier Keys section below)
  - `key`: Key code (see Key Codes section below)
- `description`: A brief description of the overlay (shown in tooltips)

## Python Overlay Format

For more advanced overlays, you can create a Python module that defines a class inheriting from the `Overlay` base class. Create a Python file in the overlays directory with the following structure:

```python
from macos_multi_overlay.overlays.base import Overlay

class MyCustomOverlay(Overlay):
    id = "my_custom"
    name = "My Custom Overlay"
    url = "https://example.com"
    icon_path = "/path/to/icon.png"
    default_hotkey = {
        "flags": 524288,  # Option key
        "key": 49         # Space key
    }
    description = "My custom overlay description"
    
    # You can add custom methods here if needed
```

## Modifier Keys

The `flags` field in the `defaultHotkey` configuration uses the following values:

- Shift: 131072 (kCGEventFlagMaskShift)
- Control: 262144 (kCGEventFlagMaskControl)
- Option/Alt: 524288 (kCGEventFlagMaskAlternate)
- Command: 1048576 (kCGEventFlagMaskCommand)

You can combine these values by adding them together. For example, Option+Command would be 524288 + 1048576 = 1572864.

## Key Codes

The `key` field in the `defaultHotkey` configuration uses the following common key codes:

- Space: 49
- Return/Enter: 36
- Escape: 53
- Arrow keys: Left (123), Right (124), Down (125), Up (126)
- Function keys: F1 (122), F2 (120), F3 (99), F4 (118), etc.
- Letters: Use the ASCII code (e.g., 'a' is 0)

## Icon Requirements

Icons should be:
- Square aspect ratio (1:1)
- At least 64x64 pixels (128x128 recommended)
- PNG format with transparency
- Visible on both light and dark backgrounds

## Examples

### Example 1: Simple JSON Overlay

```json
{
  "id": "perplexity",
  "name": "Perplexity",
  "url": "https://perplexity.ai",
  "iconPath": "/Users/username/Pictures/perplexity_icon.png",
  "defaultHotkey": {
    "flags": 786432,
    "key": 49
  },
  "description": "Perplexity AI search assistant"
}
```

### Example 2: Python Class Overlay

```python
from macos_multi_overlay.overlays.base import Overlay

class BingOverlay(Overlay):
    id = "bing"
    name = "Bing Chat"
    url = "https://www.bing.com/chat"
    icon_path = "/Users/username/Pictures/bing_icon.png"
    default_hotkey = {
        "flags": 655360,  # Option+Control
        "key": 49         # Space key
    }
    description = "Bing Chat AI assistant by Microsoft"
```

## Troubleshooting

If your overlay doesn't appear in the application:

1. Check that the JSON or Python file is in the correct directory
2. Verify that all required fields are present and correctly formatted
3. Ensure the icon file exists at the specified path
4. Restart the application to reload overlays
5. Check the application logs for any error messages

## Advanced Customization

For advanced customization beyond what's covered in this document, you can modify the source code directly. The overlay system is designed to be extensible and modular.
