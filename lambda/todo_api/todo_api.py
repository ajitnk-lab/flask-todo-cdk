"""
Flask Todo API Application

This module implements a Flask application that provides REST API endpoints for todo operations.
It integrates with DynamoDB for CRUD operations on todo items.
"""

from flask import Flask, request, jsonify
import json
import os
from flask_cors import CORS
import logging
from datetime import datetime

# Import custom modules
from .models import TodoModel
from .database import TodoDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS for web frontend integration
CORS(app)

# Initialize database
db = TodoDatabase()

# API Endpoints
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Verify DynamoDB connection
        is_connected = db.check_connection()
        
        return jsonify({
            "status": "healthy" if is_connected else "unhealthy",
            "timestamp": TodoModel.get_timestamp(),
            "database": "connected" if is_connected else "disconnected",
            "table": db.table_name
        }), 200 if is_connected else 500
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "timestamp": TodoModel.get_timestamp(),
            "error": str(e)
        }), 500

@app.route('/todos', methods=['GET'])
def list_todos():
    """
    List all todos with optional status filter and pagination.
    
    Query parameters:
    - status: Filter by status (pending, completed, archived)
    - limit: Maximum number of items to return
    - next_token: Token for pagination
    """
    try:
        # Get query parameters
        status = request.args.get('status')
        limit = request.args.get('limit', 50)
        next_token = request.args.get('next_token')
        
        try:
            limit = int(limit)
            if limit < 1 or limit > 100:
                limit = 50
        except ValueError:
            limit = 50
        
        # Validate status if provided
        if status and status not in TodoModel.VALID_STATUSES:
            return jsonify({"error": f"Invalid status. Must be one of: {', '.join(TodoModel.VALID_STATUSES)}"}), 400
        
        # Get todos from database
        result = db.list_todos(status=status, limit=limit, next_token=next_token)
        
        logger.info(f"Retrieved {result['count']} todos")
        return jsonify(result), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error in list_todos: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/todos/<todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Get a specific todo by ID."""
    try:
        todo = db.get_todo(todo_id)
        
        if not todo:
            return jsonify({"error": "Todo not found"}), 404
        
        logger.info(f"Retrieved todo {todo_id}")
        return jsonify(todo), 200
    
    except Exception as e:
        logger.error(f"Error in get_todo: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/todos', methods=['POST'])
def create_todo():
    """Create a new todo."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate input
        is_valid, error = TodoModel.validate(data)
        if not is_valid:
            return jsonify({"error": error}), 400
        
        # Create todo item using the model
        try:
            todo_item = TodoModel.from_dict(data)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
        # Save to database
        created_todo = db.create_todo(todo_item)
        
        logger.info(f"Created todo {created_todo['todo_id']}")
        return jsonify(created_todo), 201
    
    except Exception as e:
        logger.error(f"Error in create_todo: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/todos/<todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update an existing todo."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate input
        is_valid, error = TodoModel.validate(data, is_update=True)
        if not is_valid:
            return jsonify({"error": error}), 400
        
        # Check if todo exists
        existing_todo = db.get_todo(todo_id)
        if not existing_todo:
            return jsonify({"error": "Todo not found"}), 404
        
        # Add updated timestamp
        data['updated_at'] = TodoModel.get_timestamp()
        
        # Update in database
        updated_todo = db.update_todo(todo_id, data)
        
        logger.info(f"Updated todo {todo_id}")
        return jsonify(updated_todo), 200
    
    except Exception as e:
        logger.error(f"Error in update_todo: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo."""
    try:
        # Check if todo exists
        existing_todo = db.get_todo(todo_id)
        if not existing_todo:
            return jsonify({"error": "Todo not found"}), 404
        
        # Delete from database
        db.delete_todo(todo_id)
        
        logger.info(f"Deleted todo {todo_id}")
        return jsonify({"message": f"Todo {todo_id} deleted successfully"}), 200
    
    except Exception as e:
        logger.error(f"Error in delete_todo: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


# Lambda handler function
def handler(event, context):
    """
    AWS Lambda handler function.
    
    This function processes API Gateway events and forwards them to the Flask application.
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Process the API Gateway event
    from awsgi import response
    
    return response(app, event, context)

# For local development
if __name__ == '__main__':
    app.run(debug=True)