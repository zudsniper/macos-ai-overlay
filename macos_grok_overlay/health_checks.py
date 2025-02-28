import os
import sys
import time
import tempfile
import traceback
import functools
import platform
import objc


# Settings for crash loop detection.
CRASH_COUNTER_FILE = os.path.join(tempfile.gettempdir(), "macos_grok_overlay_crash_counter.txt")
CRASH_THRESHOLD = 3    # Maximum allowed crashes within the time window.
CRASH_TIME_WINDOW = 60 # Time window in seconds.


# Returns a string containing the macOS version, Python version, and PyObjC version.
def get_system_info():
    macos_version = platform.mac_ver()[0]
    python_version = platform.python_version()
    pyobjc_version = getattr(objc, '__version__', 'unknown')
    info = (
        "System Information:\n"
        f"macOS version: {macos_version}\n"
        f"Python version: {python_version}\n"
        f"PyObjC version: {pyobjc_version}\n\n"
    )
    return info

# Reads and updates the crash counter; exits if a crash loop is detected.
def check_crash_loop():
    current_time = time.time()
    count = 0
    last_time = 0

    # Read previous crash info if it exists.
    if os.path.exists(CRASH_COUNTER_FILE):
        try:
            with open(CRASH_COUNTER_FILE, "r") as f:
                line = f.read().strip()
                if line:
                    last_time_str, count_str = line.split(",")
                    last_time = float(last_time_str)
                    count = int(count_str)
        except Exception:
            # On any error, reset the counter.
            count = 0

    # If the last crash was within the time window, increment; otherwise, reset.
    if current_time - last_time < CRASH_TIME_WINDOW:
        count += 1
    else:
        count = 1

    # Write the updated crash info back to the file.
    try:
        with open(CRASH_COUNTER_FILE, "w") as f:
            f.write(f"{current_time},{count}")
    except Exception as e:
        print("Warning: Could not update crash counter file:", e)

    # If the count exceeds the threshold, abort further restarts.
    if count > CRASH_THRESHOLD:
        print("ERROR: Crash loop detected (more than {} crashes within {} seconds). Aborting further restarts.".format(CRASH_THRESHOLD, CRASH_TIME_WINDOW))
        sys.exit(1)

# Resets the crash counter after a successful run.
def reset_crash_counter():
    if os.path.exists(CRASH_COUNTER_FILE):
        try:
            os.remove(CRASH_COUNTER_FILE)
        except Exception as e:
            print("Warning: Could not reset crash counter file:", e)

# Decorator to wrap the main function with crash loop detection and error logging.
# If the wrapped function raises an exception, the error is logged (with system info)
# and printed to the terminal before exiting.
def health_check_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        check_crash_loop()
        try:
            result = func(*args, **kwargs)
            reset_crash_counter()
            print("SUCCESS")
            return result
        except Exception:
            log_path = os.path.join(tempfile.gettempdir(), "macos_grok_overlay_error_log.txt")
            system_info = get_system_info()
            error_trace = traceback.format_exc()
            with open(log_path, "w") as log_file:
                log_file.write("An unhandled exception occurred:\n")
                log_file.write(system_info)
                log_file.write(error_trace)
            print("ERROR: Application failed to start properly. Details:")
            print(system_info)
            print(error_trace)
            print(f"Error log saved at: {log_path}", flush=True)
            sys.exit(1)
    return wrapper
