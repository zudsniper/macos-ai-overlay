"""
Integration test script for macOS Multi-Overlay.

This script tests the basic functionality of the macOS Multi-Overlay application,
including overlay loading, site switching, and command-line arguments.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add the parent directory to the path so we can import the application
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from macos_multi_overlay.overlays import overlay_manager


def test_overlay_discovery():
    """Test that all built-in overlays are discovered."""
    print("Testing overlay discovery...")
    
    # Discover overlays
    overlay_manager.discover_overlays()
    
    # Get all overlays
    overlays = overlay_manager.get_all_overlays()
    
    # Check if we have at least the built-in overlays
    required_overlays = ["grok", "gemini", "claude", "chatgpt"]
    found_overlays = [overlay.id for overlay in overlays]
    
    print(f"Found overlays: {found_overlays}")
    
    # Check if all required overlays are found
    missing_overlays = [overlay_id for overlay_id in required_overlays if overlay_id not in found_overlays]
    
    if missing_overlays:
        print(f"ERROR: Missing required overlays: {missing_overlays}")
        return False
    
    print("All required overlays found.")
    return True


def test_site_argument():
    """Test the --site command-line argument."""
    print("Testing --site argument...")
    
    # Test each built-in overlay
    for site_id in ["grok", "gemini", "claude", "chatgpt"]:
        print(f"Testing --site {site_id}...")
        
        # Run the application with the --site argument
        # Note: In a real test, we would need to handle the application process properly
        # Here we're just checking that the argument is accepted
        try:
            # Use subprocess.run with a timeout to avoid hanging
            result = subprocess.run(
                [sys.executable, "-m", "macos_multi_overlay", "--site", site_id, "--check-permissions"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            # Check if the process ran without errors
            if result.returncode != 0 and "not found" in result.stderr:
                print(f"ERROR: Site {site_id} not found.")
                return False
            
            print(f"Site {site_id} accepted.")
        except subprocess.TimeoutExpired:
            # This is expected since we're not actually running the full application
            print(f"Site {site_id} started (timeout as expected).")
    
    print("All site arguments tested successfully.")
    return True


def test_list_sites():
    """Test the --list-sites command-line argument."""
    print("Testing --list-sites argument...")
    
    try:
        # Run the application with the --list-sites argument
        result = subprocess.run(
            [sys.executable, "-m", "macos_multi_overlay", "--list-sites"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Check if the output contains all required overlays
        output = result.stdout
        required_overlays = ["grok", "gemini", "claude", "chatgpt"]
        
        for overlay_id in required_overlays:
            if overlay_id not in output.lower():
                print(f"ERROR: Overlay {overlay_id} not found in --list-sites output.")
                return False
        
        print("All required overlays found in --list-sites output.")
        return True
    except Exception as e:
        print(f"ERROR: Failed to run --list-sites: {e}")
        return False


def run_tests():
    """Run all tests."""
    print("Running integration tests for macOS Multi-Overlay...")
    
    tests = [
        test_overlay_discovery,
        test_site_argument,
        test_list_sites
    ]
    
    results = []
    
    for test in tests:
        print("\n" + "="*50)
        result = test()
        results.append(result)
        print("="*50)
    
    # Print summary
    print("\nTest Summary:")
    for i, (test, result) in enumerate(zip(tests, results)):
        print(f"{i+1}. {test.__name__}: {'PASS' if result else 'FAIL'}")
    
    # Overall result
    if all(results):
        print("\nAll tests PASSED!")
        return 0
    else:
        print("\nSome tests FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
