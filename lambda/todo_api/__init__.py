"""
Flask Todo API package.

This package contains the Flask application code for the todo API,
including the API endpoints, database integration, and Lambda handler.
"""

# Import the main components for easier access
from .todo_api import app
from .lambda_handler import handler
from .models import TodoModel
from .database import TodoDatabase

__all__ = ['app', 'handler', 'TodoModel', 'TodoDatabase']