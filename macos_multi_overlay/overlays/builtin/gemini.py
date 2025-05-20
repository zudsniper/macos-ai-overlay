"""
Gemini overlay implementation for macOS Multi-Overlay.

This module provides the Gemini overlay implementation.
"""

from ..base import Overlay


class GeminiOverlay(Overlay):
    """Gemini overlay implementation.
    
    This class provides the Gemini overlay implementation with default
    settings for URL, icon, and hotkey.
    """
    
    id = "gemini"
    name = "Gemini"
    url = "https://gemini.google.com"
    icon_path = "../../images/gemini_logo.png"
    default_hotkey = {
        "flags": 786432,  # Option+Command keys (kCGEventFlagMaskAlternate | kCGEventFlagMaskCommand)
        "key": 49         # Space key
    }
    description = "Gemini AI assistant by Google"
