"""
Main CDK Stack for Flask Todo Application

This stack contains all the infrastructure components for the serverless
Flask todo application including Lambda functions, API Gateway, and DynamoDB.
"""

from aws_cdk import (
    Stack,
    CfnOutput,
    Tags,
)
from constructs import Construct
from .database_stack import DatabaseStack


class TodoStack(Stack):
    """
    Main CDK Stack for Flask Todo Application
    
    This stack integrates multiple infrastructure components:
    - DynamoDB table for todo storage (Issue #2) ✅
    - Lambda function for Flask application (Issue #3) - TODO
    - API Gateway for REST API (Issue #4) - TODO
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get environment from context or default to 'dev'
        environment = self.node.try_get_context("environment") or "dev"

        # Create database stack
        self.database_stack = DatabaseStack(
            scope, f"DatabaseStack-{environment}",
            **kwargs
        )

        # Add stack-level tags
        Tags.of(self).add("Project", "FlaskTodoCDK")
        Tags.of(self).add("Environment", environment)
        Tags.of(self).add("ManagedBy", "CDK")

        # Future components will be added here
        # TODO: Issue #3 - Add Lambda function with DynamoDB integration
        # TODO: Issue #4 - Add API Gateway
        # TODO: Issue #5 - Add CloudFront distribution
        # TODO: Issue #6 - Add monitoring and logging
        # TODO: Issue #7 - Add deployment pipeline
        
        # Output current implementation status
        CfnOutput(
            self,
            "StackStatus",
            value="Database infrastructure implemented - ready for Lambda integration",
            description="Current status of the Flask Todo CDK stack"
        )

        # Export database information for other stacks
        CfnOutput(
            self,
            "DatabaseStackReference",
            value=f"DatabaseStack-{environment}",
            description="Reference to the database stack for cross-stack integration"
        )

    @property
    def todo_table_name(self) -> str:
        """Return the DynamoDB table name for Lambda integration."""
        return self.database_stack.table_name

    @property
    def todo_table_arn(self) -> str:
        """Return the DynamoDB table ARN for Lambda integration."""
        return self.database_stack.table_arn

    @property
    def lambda_role_arn(self) -> str:
        """Return the Lambda role ARN for function creation."""
        return self.database_stack.lambda_role_arn