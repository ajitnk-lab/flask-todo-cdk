"""
Todo API Data Models

This module defines the data models and validation logic for the Todo API.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple


class TodoModel:
    """Todo item data model with validation logic."""
    
    # Valid status values
    VALID_STATUSES = ['pending', 'completed', 'archived']
    
    @staticmethod
    def generate_id() -> str:
        """Generate a unique ID for a todo item."""
        return str(uuid.uuid4())
    
    @staticmethod
    def get_timestamp() -> str:
        """Get the current timestamp in ISO 8601 format."""
        return datetime.utcnow().isoformat()
    
    @classmethod
    def validate(cls, data: Dict[str, Any], is_update: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Validate todo item data.
        
        Args:
            data: The todo data to validate
            is_update: Whether this is an update operation
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # For updates, we don't require all fields
        if not is_update and 'title' not in data:
            return False, "Title is required"
        
        if 'title' in data and (not data['title'] or len(data['title']) > 200):
            return False, "Title must be between 1 and 200 characters"
        
        if 'description' in data and data['description'] and len(data['description']) > 1000:
            return False, "Description must be less than 1000 characters"
        
        if 'status' in data and data['status'] not in cls.VALID_STATUSES:
            return False, f"Status must be one of: {', '.join(cls.VALID_STATUSES)}"
        
        return True, None
    
    @classmethod
    def create(cls, title: str, description: str = "", status: str = "pending") -> Dict[str, Any]:
        """
        Create a new todo item.
        
        Args:
            title: The todo title
            description: The todo description
            status: The todo status
            
        Returns:
            A dictionary representing the todo item
        """
        timestamp = cls.get_timestamp()
        return {
            'todo_id': cls.generate_id(),
            'title': title,
            'description': description,
            'status': status,
            'created_at': timestamp,
            'updated_at': timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a todo item from a dictionary, validating and setting defaults.
        
        Args:
            data: The dictionary data
            
        Returns:
            A validated todo item dictionary
        """
        is_valid, error = cls.validate(data)
        if not is_valid:
            raise ValueError(error)
        
        timestamp = cls.get_timestamp()
        return {
            'todo_id': cls.generate_id(),
            'title': data['title'],
            'description': data.get('description', ''),
            'status': data.get('status', 'pending'),
            'created_at': timestamp,
            'updated_at': timestamp
        }