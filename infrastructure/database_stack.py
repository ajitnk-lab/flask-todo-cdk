"""
DynamoDB Stack for Flask Todo Application

This stack creates the DynamoDB table infrastructure for storing todo items
with proper GSI configuration and IAM permissions for Lambda access.
"""

from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    RemovalPolicy,
    CfnOutput,
    Tags
)
from constructs import Construct


class DatabaseStack(Stack):
    """
    DatabaseStack creates DynamoDB table infrastructure for todo storage.
    
    Features:
    - TodoTable with partition key and attributes
    - StatusDateIndex GSI for querying by status and date
    - IAM permissions for Lambda access
    - Environment-specific configuration
    - Point-in-time recovery and CloudWatch metrics
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get environment from context or default to 'dev'
        environment = self.node.try_get_context("environment") or "dev"
        
        # Configure billing mode based on environment
        billing_mode = (
            dynamodb.BillingMode.PAY_PER_REQUEST if environment == "dev" 
            else dynamodb.BillingMode.PROVISIONED
        )
        
        # Create DynamoDB table for todos
        self.todo_table = dynamodb.Table(
            self, "TodoTable",
            table_name=f"flask-todo-{environment}",
            partition_key=dynamodb.Attribute(
                name="todo_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=billing_mode,
            # Enable point-in-time recovery for data protection
            point_in_time_recovery_specification=dynamodb.PointInTimeRecoverySpecification(
                point_in_time_recovery_enabled=True
            ),
            # Configure removal policy based on environment
            removal_policy=(
                RemovalPolicy.DESTROY if environment == "dev" 
                else RemovalPolicy.RETAIN
            ),
            # Enable CloudWatch metrics
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES if environment == "prod" else None
        )

        # Add provisioned throughput for production environment
        if environment == "prod" and billing_mode == dynamodb.BillingMode.PROVISIONED:
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
                read_capacity=5,
                write_capacity=5,
                projection_type=dynamodb.ProjectionType.ALL
            )
        else:
            # Add GSI for querying by status and creation date
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
                projection_type=dynamodb.ProjectionType.ALL
            )

        # Create IAM role for Lambda functions to access DynamoDB
        self.lambda_dynamodb_role = iam.Role(
            self, "LambdaDynamoDBRole",
            role_name=f"flask-todo-lambda-dynamodb-role-{environment}",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ]
        )

        # Create custom policy for DynamoDB operations
        dynamodb_policy = iam.Policy(
            self, "DynamoDBAccessPolicy",
            policy_name=f"flask-todo-dynamodb-policy-{environment}",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
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
                        f"{self.todo_table.table_arn}/index/*"
                    ]
                )
            ]
        )

        # Attach policy to role
        self.lambda_dynamodb_role.attach_inline_policy(dynamodb_policy)

        # Add tags for resource management
        Tags.of(self.todo_table).add("Project", "flask-todo-cdk")
        Tags.of(self.todo_table).add("Environment", environment)
        Tags.of(self.todo_table).add("Component", "database")
        Tags.of(self.lambda_dynamodb_role).add("Project", "flask-todo-cdk")
        Tags.of(self.lambda_dynamodb_role).add("Environment", environment)
        Tags.of(self.lambda_dynamodb_role).add("Component", "iam")

        # Export table information as stack outputs
        CfnOutput(
            self, "TodoTableName",
            value=self.todo_table.table_name,
            description="Name of the DynamoDB table for todos",
            export_name=f"flask-todo-table-name-{environment}"
        )

        CfnOutput(
            self, "TodoTableArn",
            value=self.todo_table.table_arn,
            description="ARN of the DynamoDB table for todos",
            export_name=f"flask-todo-table-arn-{environment}"
        )

        CfnOutput(
            self, "LambdaDynamoDBRoleArn",
            value=self.lambda_dynamodb_role.role_arn,
            description="ARN of the IAM role for Lambda DynamoDB access",
            export_name=f"flask-todo-lambda-role-arn-{environment}"
        )

        CfnOutput(
            self, "StatusDateIndexName",
            value="StatusDateIndex",
            description="Name of the GSI for querying by status and date",
            export_name=f"flask-todo-gsi-name-{environment}"
        )

    @property
    def table_name(self) -> str:
        """Return the table name for cross-stack references."""
        return self.todo_table.table_name

    @property
    def table_arn(self) -> str:
        """Return the table ARN for cross-stack references."""
        return self.todo_table.table_arn

    @property
    def lambda_role_arn(self) -> str:
        """Return the Lambda role ARN for cross-stack references."""
        return self.lambda_dynamodb_role.role_arn