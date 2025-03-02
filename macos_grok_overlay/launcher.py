# Python libraries.
import getpass
import os
import sys
from pathlib import Path

# Apple libraries.
import plistlib
from Foundation import NSDictionary
from ApplicationServices import AXIsProcessTrustedWithOptions, kAXTrustedCheckOptionPrompt

# Local libraries
from .constants import APP_TITLE


# Install the app as a startup application using a Launch Agent.
def install_startup():
    # Get the absolute path to the macos-*-overlay script
    username = getpass.getuser()
    plist = {
        "Label": f"com.{username}.macos{APP_TITLE.lower()}overlay",
        "ProgramArguments": [sys.executable, "-m", "macos_grok_overlay"],
        "RunAtLoad": True,
        "KeepAlive": True,  # Will be restarted automatically on failure.
    }
    launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
    launch_agents_dir.mkdir(parents=True, exist_ok=True)
    plist_path = launch_agents_dir / f"com.{username}.macos{APP_TITLE.lower()}overlay.plist"
    with open(plist_path, "wb") as f:
        plistlib.dump(plist, f)
    result = os.system(f"launchctl load {plist_path}")
    if result != 0:
        print(f"Failed to load Launch Agent with exit code {result}")
        sys.exit(1)
    print(f"Installed as startup app. Launch Agent created at {plist_path}.")
    print(f"To disable, run: macos-{APP_TITLE.lower()}-overlay --uninstall-startup")


# Uninstall the app from running at login.
def uninstall_startup():
    username = getpass.getuser()
    launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
    plist_path = launch_agents_dir / f"com.{username}.macos{APP_TITLE.lower()}overlay.plist"
    if plist_path.exists():
        try:
            os.system(f"launchctl unload {plist_path}")
            print(f"Uninstalled Launch Agent.")
        except Exception as e:
            print(f"Failed to uninstall launch agent. Encountered exception when running `launchctl unload {plist_path}`.\n{e}\n")
        print(f"Removed {plist_path}.")
        os.remove(plist_path)
    else:
        print("Launch Agent not found. Nothing to uninstall.")

# Check if the current process has Accessibility permissions.
def check_permissions(ask=True):
    print("\nChecking permission to utilize macOS Accessibility features to listen for the Option+Space keyboard sequence. If permission is not currently granted, a request will be made through the dialogue for the current executor (e.g., Terminal, python3, ...).\n", flush=True)
    options = NSDictionary.dictionaryWithObject_forKey_(
        True,
        kAXTrustedCheckOptionPrompt
    )
    is_trusted = AXIsProcessTrustedWithOptions(options if ask else None)
    return is_trusted

# Spawn a child process to check the latest permission status.
def get_updated_permission_status():
    result = subprocess.run(
        [sys.executable, sys.argv[0], "--check-permissions"],
        capture_output=True,
        text=True
    )
    return result.returncode == 0

# Wait for permissions to be granted, checking periodically.
def wait_for_permissions(max_wait_sec=120, wait_interval_sec=5):
    elapsed = 0
    while elapsed < max_wait_sec:
        if get_updated_permission_status():
            return True
        time.sleep(wait_interval_sec)
        elapsed += wait_interval_sec
    return False

# Relaunch the application with the same command used to start it.
def relaunch_application():
    if os.access(sys.argv[0], os.X_OK):
        # If sys.argv[0] is executable (e.g., an installed script), run it directly
        command = [sys.argv[0]] + sys.argv[1:]
    else:
        # Otherwise, assume it’s a Python script and run with the original interpreter
        command = [sys.executable] + sys.argv
    # Launch the new process
    subprocess.Popen(command, start_new_session=True)
    # Exit the current process (the child should continue regardless)
    sys.exit(0)

# Ensure Accessibility permissions are granted, relaunching if necessary.
def ensure_accessibility_permissions():
    # Prompt the user (this also triggers the macOS permission dialog)
    if check_permissions():  # Initial call to prompt
        return
    # Wait for permissions to be granted
    if wait_for_permissions():
        print("Permissions granted, exiting application (to be restarted automatically)...")
        sys.exit(0)
    else:
        print("Permissions not granted within the time limit. Uninstalling application, since this installation must have failed.")
        uninstall_startup()

