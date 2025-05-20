"""
Claude overlay implementation for macOS Multi-Overlay.

This module provides the Claude overlay implementation.
"""

from ..base import Overlay


class ClaudeOverlay(Overlay):
    """Claude overlay implementation.
    
    This class provides the Claude overlay implementation with default
    settings for URL, icon, and hotkey.
    """
    
    id = "claude"
    name = "Claude"
    url = "https://claude.ai"
    icon_path = "../../images/claude_logo.png"
    default_hotkey = {
        "flags": 655360,  # Option+Control keys (kCGEventFlagMaskAlternate | kCGEventFlagMaskControl)
        "key": 49         # Space key
    }
    description = "Claude AI assistant by Anthropic"
