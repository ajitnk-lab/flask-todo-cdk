"""
DynamoDB Infrastructure for Todo Application

This module defines the DynamoDB table used for storing todo items.
It includes the table definition, GSI for querying by status/date,
and IAM permissions for Lambda access.
"""

from aws_cdk import (
    Stack,
    CfnOutput,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
)
from constructs import Construct


class DatabaseStack(Stack):
    """
    DynamoDB Stack for Todo Application
    
    This stack creates a DynamoDB table for storing todo items with:
    - Partition key: todo_id (String)
    - Attributes: title, description, status, created_at, updated_at
    - GSI: StatusDateIndex (status + created_at)
    - IAM permissions for Lambda access
    """

    def __init__(self, scope: Construct, construct_id: str, is_prod: bool = False, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Define the DynamoDB table
        self.todo_table = dynamodb.Table(
            self,
            "TodoTable",
            partition_key=dynamodb.Attribute(
                name="todo_id",
                type=dynamodb.AttributeType.STRING
            ),
            # Use PAY_PER_REQUEST for dev, PROVISIONED for prod
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST if not is_prod else dynamodb.BillingMode.PROVISIONED,
            # For prod environment, set provisioned capacity
            read_capacity=is_prod and 5 or None,
            write_capacity=is_prod and 5 or None,
            # Enable point-in-time recovery
            point_in_time_recovery=True,
            # Set removal policy based on environment
            removal_policy=RemovalPolicy.RETAIN if is_prod else RemovalPolicy.DESTROY,
            # Enable server-side encryption
            encryption=dynamodb.TableEncryption.DEFAULT,
        )
        
        # Add GSI for querying by status and date
        self.todo_table.add_global_secondary_index(
            index_name="StatusDateIndex",
            partition_key=dynamodb.Attribute(
                name="status",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL,
        )
        
        # Create IAM policy for Lambda to access DynamoDB
        self.lambda_dynamodb_policy = iam.PolicyStatement(
            actions=[
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            resources=[
                self.todo_table.table_arn,
                f"{self.todo_table.table_arn}/index/*"  # Allow access to indexes
            ]
        )
        
        # Add CloudWatch metrics
        self.todo_table.metric_read_capacity_units()
        self.todo_table.metric_write_capacity_units()
        
        # Output the table name and ARN
        CfnOutput(
            self,
            "TodoTableName",
            value=self.todo_table.table_name,
            description="Name of the DynamoDB table for todo items",
            export_name=f"{construct_id}-TodoTableName"
        )
        
        CfnOutput(
            self,
            "TodoTableArn",
            value=self.todo_table.table_arn,
            description="ARN of the DynamoDB table for todo items",
            export_name=f"{construct_id}-TodoTableArn"
        )