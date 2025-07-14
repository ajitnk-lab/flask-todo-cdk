"""
Flask Todo API Application

This module provides REST API endpoints for todo operations using Flask and DynamoDB.
Designed to run on AWS Lambda with proper error handling and CORS support.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import json
import uuid
from datetime import datetime
import os
import logging
from botocore.exceptions import ClientError
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# DynamoDB configuration
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TODO_TABLE_NAME', 'flask-todo-dev')
table = dynamodb.Table(table_name)

# Constants
VALID_STATUSES = ['pending', 'completed', 'archived']
MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 1000


class TodoValidationError(Exception):
    """Custom exception for todo validation errors"""
    pass


def validate_todo_data(data: Dict) -> Dict:
    """
    Validate todo data for creation/update operations
    
    Args:
        data: Dictionary containing todo data
        
    Returns:
        Validated and cleaned todo data
        
    Raises:
        TodoValidationError: If validation fails
    """
    if not isinstance(data, dict):
        raise TodoValidationError("Request body must be a JSON object")
    
    # Validate title
    title = data.get('title', '').strip()
    if not title:
        raise TodoValidationError("Title is required")
    if len(title) > MAX_TITLE_LENGTH:
        raise TodoValidationError(f"Title must be {MAX_TITLE_LENGTH} characters or less")
    
    # Validate description (optional)
    description = data.get('description', '').strip()
    if len(description) > MAX_DESCRIPTION_LENGTH:
        raise TodoValidationError(f"Description must be {MAX_DESCRIPTION_LENGTH} characters or less")
    
    # Validate status
    status = data.get('status', 'pending').lower()
    if status not in VALID_STATUSES:
        raise TodoValidationError(f"Status must be one of: {', '.join(VALID_STATUSES)}")
    
    return {
        'title': title,
        'description': description,
        'status': status
    }


def create_todo_item(todo_id: str, validated_data: Dict) -> Dict:
    """Create a new todo item with timestamps"""
    now = datetime.utcnow().isoformat() + 'Z'
    
    return {
        'todo_id': todo_id,
        'title': validated_data['title'],
        'description': validated_data['description'],
        'status': validated_data['status'],
        'created_at': now,
        'updated_at': now
    }


def handle_dynamodb_error(error: ClientError) -> Tuple[Dict, int]:
    """Handle DynamoDB errors and return appropriate HTTP responses"""
    error_code = error.response['Error']['Code']
    
    if error_code == 'ResourceNotFoundException':
        return {'error': 'Database table not found'}, 500
    elif error_code == 'ValidationException':
        return {'error': 'Invalid request data'}, 400
    elif error_code == 'ConditionalCheckFailedException':
        return {'error': 'Item not found or condition failed'}, 404
    else:
        logger.error(f"DynamoDB error: {error}")
        return {'error': 'Database operation failed'}, 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test DynamoDB connection
        table.table_status
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "table": table_name
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "error": str(e)
        }), 503


@app.route('/todos', methods=['GET'])
def list_todos():
    """List all todos with optional status filtering"""
    try:
        # Get query parameters
        status_filter = request.args.get('status', '').lower()
        limit = request.args.get('limit', '50')
        
        # Validate limit
        try:
            limit = int(limit)
            if limit < 1 or limit > 100:
                limit = 50
        except ValueError:
            limit = 50
        
        # Query todos
        if status_filter and status_filter in VALID_STATUSES:
            # Use GSI to filter by status
            response = table.query(
                IndexName='StatusDateIndex',
                KeyConditionExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': status_filter},
                Limit=limit,
                ScanIndexForward=False  # Sort by created_at descending
            )
        else:
            # Scan all items
            response = table.scan(Limit=limit)
        
        todos = response.get('Items', [])
        
        # Sort by created_at descending if not using GSI
        if not status_filter or status_filter not in VALID_STATUSES:
            todos.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify({
            'todos': todos,
            'count': len(todos),
            'status_filter': status_filter if status_filter in VALID_STATUSES else None
        })
        
    except ClientError as e:
        error_response, status_code = handle_dynamodb_error(e)
        return jsonify(error_response), status_code
    except Exception as e:
        logger.error(f"Error listing todos: {e}")
        return jsonify({'error': 'Failed to retrieve todos'}), 500


@app.route('/todos/<todo_id>', methods=['GET'])
def get_todo(todo_id: str):
    """Get a specific todo by ID"""
    try:
        response = table.get_item(Key={'todo_id': todo_id})
        
        if 'Item' not in response:
            return jsonify({'error': 'Todo not found'}), 404
        
        return jsonify(response['Item'])
        
    except ClientError as e:
        error_response, status_code = handle_dynamodb_error(e)
        return jsonify(error_response), status_code
    except Exception as e:
        logger.error(f"Error getting todo {todo_id}: {e}")
        return jsonify({'error': 'Failed to retrieve todo'}), 500


@app.route('/todos', methods=['POST'])
def create_todo():
    """Create a new todo"""
    try:
        # Validate request data
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        validated_data = validate_todo_data(data)
        
        # Create todo item
        todo_id = str(uuid.uuid4())
        todo_item = create_todo_item(todo_id, validated_data)
        
        # Save to DynamoDB
        table.put_item(Item=todo_item)
        
        logger.info(f"Created todo: {todo_id}")
        return jsonify(todo_item), 201
        
    except TodoValidationError as e:
        return jsonify({'error': str(e)}), 400
    except ClientError as e:
        error_response, status_code = handle_dynamodb_error(e)
        return jsonify(error_response), status_code
    except Exception as e:
        logger.error(f"Error creating todo: {e}")
        return jsonify({'error': 'Failed to create todo'}), 500


@app.route('/todos/<todo_id>', methods=['PUT'])
def update_todo(todo_id: str):
    """Update an existing todo"""
    try:
        # Validate request data
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        validated_data = validate_todo_data(data)
        
        # Check if todo exists
        existing_response = table.get_item(Key={'todo_id': todo_id})
        if 'Item' not in existing_response:
            return jsonify({'error': 'Todo not found'}), 404
        
        existing_todo = existing_response['Item']
        
        # Update todo item
        updated_todo = {
            'todo_id': todo_id,
            'title': validated_data['title'],
            'description': validated_data['description'],
            'status': validated_data['status'],
            'created_at': existing_todo['created_at'],
            'updated_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Save to DynamoDB
        table.put_item(Item=updated_todo)
        
        logger.info(f"Updated todo: {todo_id}")
        return jsonify(updated_todo)
        
    except TodoValidationError as e:
        return jsonify({'error': str(e)}), 400
    except ClientError as e:
        error_response, status_code = handle_dynamodb_error(e)
        return jsonify(error_response), status_code
    except Exception as e:
        logger.error(f"Error updating todo {todo_id}: {e}")
        return jsonify({'error': 'Failed to update todo'}), 500


@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id: str):
    """Delete a todo"""
    try:
        # Check if todo exists first
        existing_response = table.get_item(Key={'todo_id': todo_id})
        if 'Item' not in existing_response:
            return jsonify({'error': 'Todo not found'}), 404
        
        # Delete the todo
        table.delete_item(Key={'todo_id': todo_id})
        
        logger.info(f"Deleted todo: {todo_id}")
        return jsonify({'message': 'Todo deleted successfully'}), 200
        
    except ClientError as e:
        error_response, status_code = handle_dynamodb_error(e)
        return jsonify(error_response), status_code
    except Exception as e:
        logger.error(f"Error deleting todo {todo_id}: {e}")
        return jsonify({'error': 'Failed to delete todo'}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({'error': 'Method not allowed'}), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


# Lambda handler for AWS Lambda deployment
def lambda_handler(event, context):
    """AWS Lambda handler function"""
    try:
        from serverless_wsgi import handle_request
        return handle_request(app, event, context)
    except ImportError:
        # Fallback for local development
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'serverless_wsgi not available'})
        }


if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=5000)