"""
Initialization module for built-in overlays.

This module imports all built-in overlay implementations to ensure they
are discovered by the overlay manager.
"""

from .grok import GrokOverlay
from .gemini import GeminiOverlay
from .claude import ClaudeOverlay
from .chatgpt import ChatGPTOverlay

# Export all overlay classes
__all__ = [
    'GrokOverlay',
    'GeminiOverlay',
    'ClaudeOverlay',
    'ChatGPTOverlay',
]
