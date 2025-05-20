"""
Base overlay class definition for macOS Multi-Overlay.

This module defines the base Overlay class that all overlay implementations
must inherit from, whether they are built-in or custom overlays.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Any, Union


class Overlay:
    """Base class for all overlays.
    
    All overlay implementations must inherit from this class and provide
    the required attributes.
    
    Attributes:
        id (str): Unique identifier for the overlay.
        name (str): Display name for the overlay.
        url (str): URL to load in the overlay window.
        icon_path (str): Path to the overlay icon.
        default_hotkey (Dict): Default hotkey configuration.
        description (str, optional): Description of the overlay.
    """
    
    id: str = ""
    name: str = ""
    url: str = ""
    icon_path: str = ""
    default_hotkey: Dict[str, Any] = {}
    description: str = ""
    
    def __init__(self, **kwargs):
        """Initialize an overlay instance.
        
        Args:
            **kwargs: Keyword arguments to override class attributes.
        """
        # Override class attributes with instance attributes if provided
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'Overlay':
        """Create an overlay instance from JSON data.
        
        Args:
            json_data: Dictionary containing overlay metadata.
            
        Returns:
            Overlay: A new overlay instance.
            
        Raises:
            ValueError: If required fields are missing.
        """
        required_fields = ['id', 'name', 'url', 'iconPath']
        missing_fields = [field for field in required_fields if field not in json_data]
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Map JSON fields to class attributes
        kwargs = {
            'id': json_data['id'],
            'name': json_data['name'],
            'url': json_data['url'],
            'icon_path': json_data['iconPath'],
        }
        
        # Add optional fields if present
        if 'defaultHotkey' in json_data:
            kwargs['default_hotkey'] = json_data['defaultHotkey']
        
        if 'description' in json_data:
            kwargs['description'] = json_data['description']
        
        return cls(**kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the overlay to a dictionary.
        
        Returns:
            Dict: Dictionary representation of the overlay.
        """
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'iconPath': self.icon_path,
            'defaultHotkey': self.default_hotkey,
            'description': self.description,
        }
    
    def validate(self) -> bool:
        """Validate that the overlay has all required attributes.
        
        Returns:
            bool: True if valid, False otherwise.
        """
        return all([
            self.id,
            self.name,
            self.url,
            self.icon_path,
        ])
    
    def get_absolute_icon_path(self, base_dir: Optional[str] = None) -> str:
        """Get the absolute path to the overlay icon.
        
        Args:
            base_dir: Base directory to resolve relative paths against.
                     If None, uses the directory of the overlay module.
                     
        Returns:
            str: Absolute path to the icon.
        """
        if os.path.isabs(self.icon_path):
            return self.icon_path
        
        if base_dir is None:
            # Use the directory of the overlay module
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        return os.path.abspath(os.path.join(base_dir, self.icon_path))
