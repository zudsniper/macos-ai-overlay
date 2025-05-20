"""
ChatGPT overlay implementation for macOS Multi-Overlay.

This module provides the ChatGPT overlay implementation.
"""

from ..base import Overlay


class ChatGPTOverlay(Overlay):
    """ChatGPT overlay implementation.
    
    This class provides the ChatGPT overlay implementation with default
    settings for URL, icon, and hotkey.
    """
    
    id = "chatgpt"
    name = "ChatGPT"
    url = "https://chat.openai.com"
    icon_path = "../../images/chatgpt_logo.png"
    default_hotkey = {
        "flags": 917504,  # Option+Shift keys (kCGEventFlagMaskAlternate | kCGEventFlagMaskShift)
        "key": 49         # Space key
    }
    description = "ChatGPT AI assistant by OpenAI"
