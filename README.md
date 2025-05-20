# macOS Multi-Overlay

A macOS application that provides a floating overlay window for multiple AI assistants, including Grok, Gemini, Claude, and ChatGPT. Each overlay can be summoned and dismissed with customizable keyboard shortcuts.

## Features

- **Multiple AI Assistant Support**: Built-in support for Grok, Gemini, Claude, and ChatGPT
- **Plugin Architecture**: Easily add custom overlays via JSON or Python files
- **Customizable Hotkeys**: Set individual keyboard shortcuts for each overlay
- **Unified Launch Menu**: Access all overlays from a single hotkey-triggered menu
- **Menu Bar Integration**: Quick access to all overlays from the menu bar
- **Persistent Window Position**: Window position and size are remembered between sessions
- **Auto-launch Option**: Optionally start the application at login

## Installation

### Prerequisites

- macOS 10.15 (Catalina) or later
- Python 3.7 or later

### Installation Steps

1. Clone this repository:
   ```
   git clone https://github.com/zudsniper/macos-multi-overlay.git
   cd macos-multi-overlay
   ```

2. Install the package:
   ```
   pip install -e .
   ```

3. Run the application:
   ```
   macos-multi-overlay
   ```

## Usage

### Command Line Options

```
macos-multi-overlay [options]

Options:
  --site SITE_ID       Specify which overlay to launch (e.g., grok, gemini, claude, chatgpt)
  --list-sites         List all available overlay sites
  --install-startup    Install the app to run at login
  --uninstall-startup  Uninstall the app from running at login
  --check-permissions  Check Accessibility permissions only
```

### Keyboard Shortcuts

By default, each overlay has its own keyboard shortcut:

- **Grok**: Option + Space
- **Gemini**: Option + Command + Space
- **Claude**: Option + Control + Space
- **ChatGPT**: Option + Shift + Space
- **Overlay Selector**: Option + Shift + Space (shows a menu of all available overlays)

You can customize these shortcuts through the menu bar options.

### Adding Custom Overlays

You can add custom overlays by creating JSON or Python files. See the [Overlay Plugin API Documentation](docs/OVERLAYS.md) for details.

#### Example JSON Overlay

Create a file in `~/Library/Application Support/macOS Multi-Overlay/overlays/` with the following content:

```json
{
  "id": "perplexity",
  "name": "Perplexity",
  "url": "https://perplexity.ai",
  "iconPath": "/path/to/icon.png",
  "defaultHotkey": {
    "flags": 786432,
    "key": 49
  },
  "description": "Perplexity AI search assistant"
}
```

## Menu Bar Options

The menu bar icon provides access to:

- **Launch Overlay**: Submenu with all available overlays
- **Show Overlay Selector**: Opens the overlay selector menu at the cursor position
- **Set Overlay Selector Hotkey**: Change the hotkey for the overlay selector
- **Clear Web Cache**: Clear cookies and cache data for all overlays
- **Install/Uninstall Autolauncher**: Configure the app to run at login
- **Quit**: Exit the application

## Permissions

The application requires Accessibility permissions to function properly. When you first run the application, macOS will prompt you to grant these permissions. You can also grant them manually in System Preferences > Security & Privacy > Privacy > Accessibility.

## Development

### Running Tests

```
python -m unittest discover tests
```

### Project Structure

- `macos_multi_overlay/`: Main package
  - `overlays/`: Overlay definitions and loader
    - `builtin/`: Built-in overlay implementations
    - `custom/`: Directory for user-added overlays
  - `config/`: Configuration management
  - `ui/`: UI components
- `docs/`: Documentation
- `tests/`: Unit and integration tests

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This project is a fork of the [macOS Grok Overlay](https://github.com/tchlux/macos-grok-overlay) by tchlux, extended to support multiple AI assistants.
