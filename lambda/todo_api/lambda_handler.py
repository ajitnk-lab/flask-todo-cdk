"""
AWS Lambda Handler for Todo API

This module provides the AWS Lambda handler function that integrates
the Flask application with API Gateway.
"""

import json
import logging
from awsgi import response
from .todo_api import app

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    AWS Lambda handler function.
    
    This function processes API Gateway events and forwards them to the Flask application.
    
    Args:
        event: The event dict from API Gateway
        context: The Lambda context object
        
    Returns:
        The API Gateway response
    """
    # Log the incoming event for debugging
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Process the API Gateway event with the Flask app
    return response(app, event, context)