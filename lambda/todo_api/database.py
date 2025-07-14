"""
Todo API Database Operations

This module handles all DynamoDB operations for the Todo API.
"""

import boto3
import os
import json
import logging
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger(__name__)

class TodoDatabase:
    """Class for handling DynamoDB operations for todos."""
    
    def __init__(self, table_name: Optional[str] = None, region: Optional[str] = None):
        """
        Initialize the database connection.
        
        Args:
            table_name: The DynamoDB table name (defaults to environment variable)
            region: The AWS region (defaults to environment variable)
        """
        self.table_name = table_name or os.environ.get('TODO_TABLE_NAME', 'flask-todo-dev')
        self.region = region or os.environ.get('AWS_REGION', 'us-east-1')
        self.status_date_index = os.environ.get('STATUS_DATE_INDEX', 'StatusDateIndex')
        
        # Initialize DynamoDB resource
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
        self.table = self.dynamodb.Table(self.table_name)
        
        logger.info(f"Initialized TodoDatabase with table: {self.table_name}, region: {self.region}")
    
    def get_todo(self, todo_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a todo item by ID.
        
        Args:
            todo_id: The ID of the todo to retrieve
            
        Returns:
            The todo item or None if not found
        """
        try:
            response = self.table.get_item(
                Key={
                    'todo_id': todo_id
                }
            )
            return response.get('Item')
        except ClientError as e:
            logger.error(f"Error getting todo {todo_id}: {str(e)}")
            raise
    
    def create_todo(self, todo_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new todo item.
        
        Args:
            todo_item: The todo item to create
            
        Returns:
            The created todo item
        """
        try:
            self.table.put_item(Item=todo_item)
            return todo_item
        except ClientError as e:
            logger.error(f"Error creating todo: {str(e)}")
            raise
    
    def update_todo(self, todo_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a todo item.
        
        Args:
            todo_id: The ID of the todo to update
            updates: The fields to update
            
        Returns:
            The updated todo item
        """
        try:
            # Prepare update expression
            update_expressions = []
            expression_attribute_values = {}
            expression_attribute_names = {}
            
            # Add fields to update
            for key, value in updates.items():
                if key not in ['todo_id', 'created_at']:  # Don't update these fields
                    if key == 'title':  # 'title' is a reserved word in DynamoDB
                        update_expressions.append('#title = :title')
                        expression_attribute_values[':title'] = value
                        expression_attribute_names['#title'] = 'title'
                    else:
                        update_expressions.append(f"{key} = :{key}")
                        expression_attribute_values[f":{key}"] = value
            
            # Perform update
            update_expression = 'SET ' + ', '.join(update_expressions)
            
            response = self.table.update_item(
                Key={
                    'todo_id': todo_id
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ExpressionAttributeNames=expression_attribute_names if expression_attribute_names else None,
                ReturnValues='ALL_NEW'
            )
            
            return response.get('Attributes', {})
        except ClientError as e:
            logger.error(f"Error updating todo {todo_id}: {str(e)}")
            raise
    
    def delete_todo(self, todo_id: str) -> bool:
        """
        Delete a todo item.
        
        Args:
            todo_id: The ID of the todo to delete
            
        Returns:
            True if successful
        """
        try:
            self.table.delete_item(
                Key={
                    'todo_id': todo_id
                }
            )
            return True
        except ClientError as e:
            logger.error(f"Error deleting todo {todo_id}: {str(e)}")
            raise
    
    def list_todos(self, status: Optional[str] = None, limit: int = 50, 
                  next_token: Optional[str] = None) -> Dict[str, Any]:
        """
        List todo items with optional filtering and pagination.
        
        Args:
            status: Filter by status
            limit: Maximum number of items to return
            next_token: Token for pagination
            
        Returns:
            Dictionary with todos and pagination info
        """
        try:
            # Prepare scan parameters
            scan_params = {
                'Limit': limit
            }
            
            if next_token:
                try:
                    scan_params['ExclusiveStartKey'] = json.loads(next_token)
                except json.JSONDecodeError:
                    raise ValueError("Invalid pagination token")
            
            # If status is provided, use the GSI to query by status
            if status:
                # Use query instead of scan for better performance
                response = self.table.query(
                    IndexName=self.status_date_index,
                    KeyConditionExpression="status = :status",
                    ExpressionAttributeValues={
                        ":status": status
                    },
                    Limit=limit,
                    **({'ExclusiveStartKey': scan_params['ExclusiveStartKey']} if 'ExclusiveStartKey' in scan_params else {})
                )
            else:
                # Scan all todos if no status filter
                response = self.table.scan(**scan_params)
            
            # Prepare response
            result = {
                "todos": response.get('Items', []),
                "count": len(response.get('Items', [])),
                "total_scanned": response.get('ScannedCount', 0)
            }
            
            # Add pagination token if more results exist
            if 'LastEvaluatedKey' in response:
                result['next_token'] = json.dumps(response['LastEvaluatedKey'])
            
            return result
        except ClientError as e:
            logger.error(f"Error listing todos: {str(e)}")
            raise
    
    def check_connection(self) -> bool:
        """
        Check if the database connection is working.
        
        Returns:
            True if connection is working
        """
        try:
            # Verify DynamoDB connection by describing the table
            dynamodb_client = boto3.client('dynamodb', region_name=self.region)
            dynamodb_client.describe_table(TableName=self.table_name)
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {str(e)}")
            return False