"""
Overlay discovery and registration module for macOS Multi-Overlay.

This module provides functionality to discover and register overlays from
both built-in and custom sources.
"""

import os
import json
import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Type, Any

from .base import Overlay


class OverlayManager:
    """Manager for discovering and registering overlays.
    
    This class handles the discovery and registration of overlays from
    both built-in and custom sources.
    """
    
    def __init__(self):
        """Initialize the overlay manager."""
        self.overlays: Dict[str, Overlay] = {}
        self.current_overlay_id: Optional[str] = None
    
    def discover_overlays(self) -> None:
        """Discover and register all available overlays.
        
        This method discovers and registers overlays from both built-in
        and custom sources.
        """
        # Discover built-in overlays
        self._discover_builtin_overlays()
        
        # Discover custom overlays
        self._discover_custom_overlays()
        
        # Set the default overlay if none is set
        if not self.current_overlay_id and self.overlays:
            self.current_overlay_id = next(iter(self.overlays))
    
    def _discover_builtin_overlays(self) -> None:
        """Discover and register built-in overlays.
        
        This method discovers and registers overlays from the built-in
        overlays directory.
        """
        builtin_dir = os.path.join(os.path.dirname(__file__), 'builtin')
        
        # Import all modules in the builtin directory
        for filename in os.listdir(builtin_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]  # Remove .py extension
                module_path = os.path.join(builtin_dir, filename)
                
                try:
                    # Import the module
                    spec = importlib.util.spec_from_file_location(
                        f"macos_multi_overlay.overlays.builtin.{module_name}",
                        module_path
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Find all Overlay subclasses in the module
                        for name, obj in inspect.getmembers(module):
                            if (inspect.isclass(obj) and 
                                issubclass(obj, Overlay) and 
                                obj is not Overlay):
                                # Create an instance and register it
                                overlay = obj()
                                if overlay.validate():
                                    self.register_overlay(overlay)
                except Exception as e:
                    print(f"Error loading built-in overlay {module_name}: {e}")
    
    def _discover_custom_overlays(self) -> None:
        """Discover and register custom overlays.
        
        This method discovers and registers overlays from the custom
        overlays directory.
        """
        custom_dir = os.path.join(os.path.dirname(__file__), 'custom')
        
        # Ensure the custom directory exists
        os.makedirs(custom_dir, exist_ok=True)
        
        # Process all JSON files in the custom directory
        for filename in os.listdir(custom_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(custom_dir, filename)
                
                try:
                    # Load the JSON file
                    with open(file_path, 'r') as f:
                        json_data = json.load(f)
                    
                    # Create an overlay from the JSON data
                    overlay = Overlay.from_json(json_data)
                    
                    # Set the base directory for resolving relative icon paths
                    overlay.icon_path = overlay.get_absolute_icon_path(custom_dir)
                    
                    # Register the overlay
                    if overlay.validate():
                        self.register_overlay(overlay)
                except Exception as e:
                    print(f"Error loading custom overlay {filename}: {e}")
    
    def register_overlay(self, overlay: Overlay) -> None:
        """Register an overlay.
        
        Args:
            overlay: The overlay to register.
        """
        self.overlays[overlay.id] = overlay
    
    def get_overlay(self, overlay_id: str) -> Optional[Overlay]:
        """Get an overlay by ID.
        
        Args:
            overlay_id: The ID of the overlay to get.
            
        Returns:
            The overlay with the given ID, or None if not found.
        """
        return self.overlays.get(overlay_id)
    
    def get_all_overlays(self) -> List[Overlay]:
        """Get all registered overlays.
        
        Returns:
            A list of all registered overlays.
        """
        return list(self.overlays.values())
    
    def set_current_overlay(self, overlay_id: str) -> bool:
        """Set the current overlay.
        
        Args:
            overlay_id: The ID of the overlay to set as current.
            
        Returns:
            True if the overlay was set, False if the overlay was not found.
        """
        if overlay_id in self.overlays:
            self.current_overlay_id = overlay_id
            return True
        return False
    
    def get_current_overlay(self) -> Optional[Overlay]:
        """Get the current overlay.
        
        Returns:
            The current overlay, or None if no overlay is set.
        """
        if self.current_overlay_id:
            return self.overlays.get(self.current_overlay_id)
        return None


# Create a singleton instance of the overlay manager
overlay_manager = OverlayManager()
