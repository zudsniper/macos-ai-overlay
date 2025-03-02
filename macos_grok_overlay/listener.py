# Python libraries
import json
from pathlib import Path

# Apple libraries
from Foundation import (
    NSUserNotification,
    NSUserNotificationCenter,
)
from Quartz import (
    CGEventGetFlags,
    CGEventGetIntegerValueField,
    kCGEventKeyDown,
    kCGKeyboardEventKeycode,
    NSEvent,
    NSAlternateKeyMask,
    NSCommandKeyMask,
    NSControlKeyMask,
    NSShiftKeyMask,
)

# Local libraries
from .constants import LAUNCHER_TRIGGER, LAUNCHER_TRIGGER_MASK
from .health_checks import LOG_DIR

# This is the file 
TRIGGER_FILE = LOG_DIR / "custom_trigger.json"

# Load trigger from JSON file if it exists, otherwise do nothing.
def load_custom_lancher_trigger():
    if TRIGGER_FILE.exists():
        try:
            with open(TRIGGER_FILE, "r") as f:
                data = json.load(f)
                launcher_trigger = {"flags": data["flags"], "key": data["key"]}
            print(f"Setting custom launch trigger:\n  {launcher_trigger}", flush=True)
            LAUNCHER_TRIGGER.update(launcher_trigger)
        except (json.JSONDecodeError, KeyError):
            pass

# Begin listening for a new key combination for triggering the application.
def set_custom_launcher_trigger():
    print("Setting new launcher trigger.", flush=True)
    # Disable the current listener.
    LAUNCHER_TRIGGER["flags"] = None
    LAUNCHER_TRIGGER["key"] = None
    notification = NSUserNotification.alloc().init()
    notification.setTitle_("macOS Grok Overlay")
    notification.setInformativeText_("Press the new trigger key combination now.")
    NSUserNotificationCenter.defaultUserNotificationCenter().deliverNotification_(notification)

# Announce and save a new key combination for triggering the application.
def announce_custom_launcher_trigger(event, flags, keycode):
    # Capture the new trigger
    launcher_trigger = {"flags": flags, "key": keycode}
    with open(TRIGGER_FILE, "w") as f:
        json.dump(launcher_trigger, f)
    LAUNCHER_TRIGGER.update(launcher_trigger)
    # Convert to human-readable string
    nsevent = NSEvent.eventWithCGEvent_(event)
    if nsevent:
        key = nsevent.charactersIgnoringModifiers()
        if key == " ":
            key_name = "Space"
        elif key == "\r":
            key_name = "Return"
        elif key == "\x1b":
            key_name = "Escape"
        else:
            key_name = key.upper()
    else:
        key_name = f"Keycode {keycode}"
    modifier_names = []
    if flags & NSShiftKeyMask:
        modifier_names.append("Shift")
    if flags & NSControlKeyMask:
        modifier_names.append("Control")
    if flags & NSAlternateKeyMask:
        modifier_names.append("Option")
    if flags & NSCommandKeyMask:
        modifier_names.append("Command")
    trigger_str = " + ".join(modifier_names + [key_name]) if modifier_names else key_name
    print("New launcher trigger set:", flush=True)
    print(f"  {trigger_str}", flush=True)
    # Show notification
    notification = NSUserNotification.alloc().init()
    notification.setTitle_("macOS Grok Overlay")
    notification.setInformativeText_(f"New trigger set: {trigger_str}")
    NSUserNotificationCenter.defaultUserNotificationCenter().deliverNotification_(notification)

# The logic for the global event listener for showing and hiding the application.
def global_show_hide_listener(app):
    # Define a listener (that references the given app).
    def listener(proxy, event_type, event, refcon):
        # Handle only key-down events
        if event_type == kCGEventKeyDown:
            # Extract the keycode (Space is 49)
            keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
            # Extract modifier flags (e.g., Option, Shift, etc.)
            flags = CGEventGetFlags(event) & LAUNCHER_TRIGGER_MASK
            # Check to see if we should be assigning a new key combination.
            if (None in set(LAUNCHER_TRIGGER.values())):
                print("  received keys, establishing new trigger..", flush=True)
                announce_custom_launcher_trigger(event, flags, keycode)
            # Check for Option + Space (no other modifiers)
            if (flags == LAUNCHER_TRIGGER["flags"]) and (keycode == LAUNCHER_TRIGGER["key"]):
                if app.window.isKeyWindow():
                    app.hideWindow_(None)
                else:
                    app.showWindow_(None)
                # Return None to consume the event and prevent propagation
                return None
        # Return the event unchanged if it’s not Option + Space
        return event
    return listener
