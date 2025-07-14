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


class TodoStack(Stack):
    """
    Main CDK Stack for Flask Todo Application
    
    This stack will be implemented in subsequent issues to include:
    - DynamoDB table for todo storage (Issue #2)
    - Lambda function for Flask application (Issue #4)
    - API Gateway for REST API (Issue #5)
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Add stack-level tags
        Tags.of(self).add("Project", "FlaskTodoCDK")
        Tags.of(self).add("Environment", "Development")
        Tags.of(self).add("ManagedBy", "CDK")

        # Placeholder for future components
        # TODO: Issue #2 - Add DynamoDB table
        # TODO: Issue #3 - Add Lambda function
        # TODO: Issue #4 - Add API Gateway
        
        # Output placeholder - will be updated in future issues
        CfnOutput(
            self,
            "StackStatus",
            value="Foundation created - ready for component implementation",
            description="Current status of the Flask Todo CDK stack"
        )