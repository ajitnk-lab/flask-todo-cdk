"""
Main CDK Stack for Flask Todo Application

This stack will contain all the infrastructure components for the serverless
Flask todo application including Lambda functions, API Gateway, and DynamoDB.
"""

from aws_cdk import (
    Stack,
    CfnOutput,
    Tags,
)
from constructs import Construct
from infrastructure.database_stack import DatabaseStack


class TodoStack(Stack):
    """
    Main CDK Stack for Flask Todo Application
    
    This stack includes:
    - DynamoDB table for todo storage (Issue #2)
    - Lambda function for Flask application (Issue #4) - Coming soon
    - API Gateway for REST API (Issue #5) - Coming soon
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Add stack-level tags
        Tags.of(self).add("Project", "FlaskTodoCDK")
        Tags.of(self).add("Environment", "Development")
        Tags.of(self).add("ManagedBy", "CDK")

        # Determine if this is a production environment based on stack name
        is_production = "prod" in construct_id.lower()
        
        # Create the database stack for todo storage
        self.database_stack = DatabaseStack(
            self, 
            "DatabaseStack", 
            is_production=is_production
        )
        
        # Store reference to the DynamoDB table for use by Lambda functions
        self.todo_table = self.database_stack.todo_table
        
        # TODO: Issue #3 - Add Lambda function
        # TODO: Issue #4 - Add API Gateway
        
        # Update stack output to reflect current implementation status
        CfnOutput(
            self,
            "StackStatus",
            value="DynamoDB table created - ready for Lambda implementation",
            description="Current status of the Flask Todo CDK stack"
        )