"""
DynamoDB Stack for Todo Application

This module defines the DynamoDB infrastructure for storing todo items.
It creates a table with appropriate schema, GSI, and IAM permissions.
"""

from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    RemovalPolicy,
    CfnOutput,
    Tags,
    aws_iam as iam,
)
from constructs import Construct


class DatabaseStack(Stack):
    """
    DynamoDB Stack for Todo Application
    
    Creates a DynamoDB table with the following schema:
    - Partition Key: todo_id (String)
    - Attributes:
        - todo_id: String (Primary Key)
        - title: String (Required)
        - description: String (Optional)
        - status: String (Required) # "pending", "completed", "archived"
        - created_at: String (ISO 8601 timestamp)
        - updated_at: String (ISO 8601 timestamp)
        - user_id: String (Future use for multi-user support)
    
    Also includes a GSI for querying by status and date:
    - GSI Name: StatusDateIndex
    - Partition Key: status (String)
    - Sort Key: created_at (String)
    """

    def __init__(self, scope: Construct, construct_id: str, is_production=False, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Set environment-specific configurations
        env_name = "prod" if is_production else "dev"
        table_name = f"flask-todo-table-{env_name}"
        removal_policy = RemovalPolicy.RETAIN if is_production else RemovalPolicy.DESTROY
        billing_mode = dynamodb.BillingMode.PROVISIONED if is_production else dynamodb.BillingMode.PAY_PER_REQUEST
        
        # Default provisioned capacity if using provisioned billing mode
        read_capacity = 5 if is_production else None
        write_capacity = 5 if is_production else None
        
        # DynamoDB Table for Todo items
        self.todo_table = dynamodb.Table(
            self, "TodoTable",
            table_name=table_name,
            partition_key=dynamodb.Attribute(
                name="todo_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=billing_mode,
            removal_policy=removal_policy,
            point_in_time_recovery=True,
            read_capacity=read_capacity,
            write_capacity=write_capacity,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
        )
        
        # Global Secondary Index for status-based queries
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
        
        # Add stack-level tags
        Tags.of(self).add("Project", "FlaskTodoCDK")
        Tags.of(self).add("Environment", "Production" if is_production else "Development")
        Tags.of(self).add("ManagedBy", "CDK")
        Tags.of(self).add("Component", "Database")
        
        # CloudWatch metrics are enabled by default
        
        # Stack outputs
        CfnOutput(
            self,
            "TodoTableName",
            value=self.todo_table.table_name,
            description="Name of the DynamoDB table for todo items",
            export_name=f"TodoTable-{env_name}-Name"
        )
        
        CfnOutput(
            self,
            "TodoTableArn",
            value=self.todo_table.table_arn,
            description="ARN of the DynamoDB table for todo items",
            export_name=f"TodoTable-{env_name}-Arn"
        )
    
    def grant_table_permissions(self, role):
        """
        Grant the necessary DynamoDB permissions to the provided IAM role
        
        Permissions granted:
        - dynamodb:GetItem
        - dynamodb:PutItem
        - dynamodb:UpdateItem
        - dynamodb:DeleteItem
        - dynamodb:Query
        - dynamodb:Scan
        
        Args:
            role: The IAM role to grant permissions to
        """
        self.todo_table.grant_read_data(role)
        self.todo_table.grant_write_data(role)
        
        # Additional permissions for GSI queries
        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "dynamodb:Query",
                    "dynamodb:Scan"
                ],
                resources=[
                    f"{self.todo_table.table_arn}/index/*"
                ]
            )
        )