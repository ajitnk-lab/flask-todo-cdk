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

        # Determine if this is a production environment
        is_prod = "Prod" in construct_id
        
        # Add stack-level tags
        Tags.of(self).add("Project", "FlaskTodoCDK")
        Tags.of(self).add("Environment", "Production" if is_prod else "Development")
        Tags.of(self).add("ManagedBy", "CDK")

        # Create the database stack for todo storage
        self.database_stack = DatabaseStack(
            self, 
            f"{construct_id}Database", 
            is_prod=is_prod
        )
        
        # Store references to resources for other components to use
        self.todo_table = self.database_stack.todo_table
        self.lambda_dynamodb_policy = self.database_stack.lambda_dynamodb_policy
        
        # TODO: Issue #3 - Add Lambda function
        # TODO: Issue #4 - Add API Gateway
        
        # Update output to reflect current implementation status
        CfnOutput(
            self,
            "StackStatus",
            value="DynamoDB infrastructure implemented - ready for Flask API implementation",
            description="Current status of the Flask Todo CDK stack"
        )