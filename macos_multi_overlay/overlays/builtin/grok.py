"""
Grok overlay implementation for macOS Multi-Overlay.

This module provides the Grok overlay implementation.
"""

from ..base import Overlay


class GrokOverlay(Overlay):
    """Grok overlay implementation.
    
    This class provides the Grok overlay implementation with default
    settings for URL, icon, and hotkey.
    """
    
    id = "grok"
    name = "Grok"
    url = "https://grok.com?referrer=macos-multi-overlay"
    icon_path = "../../images/grok_logo.png"
    default_hotkey = {
        "flags": 524288,  # Option key (kCGEventFlagMaskAlternate)
        "key": 49         # Space key
    }
    description = "Grok AI assistant by xAI"
