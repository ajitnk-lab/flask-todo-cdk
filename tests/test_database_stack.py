"""
Unit tests for DatabaseStack

Tests the DynamoDB infrastructure stack to ensure proper configuration
of table, GSI, IAM permissions, and cross-stack integration.
"""

import pytest
import aws_cdk as cdk
from aws_cdk import assertions
from infrastructure.database_stack import DatabaseStack


class TestDatabaseStack:
    """Test suite for DatabaseStack"""

    def setup_method(self):
        """Set up test fixtures"""
        self.app = cdk.App()
        self.stack = DatabaseStack(
            self.app, "TestDatabaseStack",
            env=cdk.Environment(region="us-east-1")
        )
        self.template = assertions.Template.from_stack(self.stack)

    def test_dynamodb_table_created(self):
        """Test that DynamoDB table is created with correct configuration"""
        self.template.has_resource_properties("AWS::DynamoDB::Table", {
            "TableName": "flask-todo-dev",
            "BillingMode": "PAY_PER_REQUEST",
            "KeySchema": [
                {
                    "AttributeName": "todo_id",
                    "KeyType": "HASH"
                }
            ],
            "AttributeDefinitions": [
                {
                    "AttributeName": "todo_id",
                    "AttributeType": "S"
                },
                {
                    "AttributeName": "status",
                    "AttributeType": "S"
                },
                {
                    "AttributeName": "created_at",
                    "AttributeType": "S"
                }
            ]
        })

    def test_global_secondary_index_created(self):
        """Test that GSI is created with correct configuration"""
        self.template.has_resource_properties("AWS::DynamoDB::Table", {
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "StatusDateIndex",
                    "KeySchema": [
                        {
                            "AttributeName": "status",
                            "KeyType": "HASH"
                        },
                        {
                            "AttributeName": "created_at",
                            "KeyType": "RANGE"
                        }
                    ],
                    "Projection": {
                        "ProjectionType": "ALL"
                    }
                }
            ]
        })

    def test_point_in_time_recovery_enabled(self):
        """Test that point-in-time recovery is enabled"""
        self.template.has_resource_properties("AWS::DynamoDB::Table", {
            "PointInTimeRecoverySpecification": {
                "PointInTimeRecoveryEnabled": True
            }
        })

    def test_iam_role_created(self):
        """Test that IAM role for Lambda is created"""
        self.template.has_resource_properties("AWS::IAM::Role", {
            "RoleName": "flask-todo-lambda-dynamodb-role-dev",
            "AssumeRolePolicyDocument": {
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        }
                    }
                ]
            }
        })

    def test_dynamodb_policy_created(self):
        """Test that DynamoDB access policy is created with correct permissions"""
        self.template.has_resource_properties("AWS::IAM::Policy", {
            "PolicyName": "flask-todo-dynamodb-policy-dev",
            "PolicyDocument": {
                "Statement": [
                    {
                        "Action": [
                            "dynamodb:GetItem",
                            "dynamodb:PutItem",
                            "dynamodb:UpdateItem",
                            "dynamodb:DeleteItem",
                            "dynamodb:Query",
                            "dynamodb:Scan"
                        ],
                        "Effect": "Allow"
                    }
                ]
            }
        })

    def test_stack_outputs_created(self):
        """Test that all required stack outputs are created"""
        # Test table name output
        self.template.has_output("TodoTableName", {
            "Description": "Name of the DynamoDB table for todos",
            "Export": {
                "Name": "flask-todo-table-name-dev"
            }
        })

        # Test table ARN output
        self.template.has_output("TodoTableArn", {
            "Description": "ARN of the DynamoDB table for todos",
            "Export": {
                "Name": "flask-todo-table-arn-dev"
            }
        })

        # Test Lambda role ARN output
        self.template.has_output("LambdaDynamoDBRoleArn", {
            "Description": "ARN of the IAM role for Lambda DynamoDB access",
            "Export": {
                "Name": "flask-todo-lambda-role-arn-dev"
            }
        })

        # Test GSI name output
        self.template.has_output("StatusDateIndexName", {
            "Description": "Name of the GSI for querying by status and date",
            "Export": {
                "Name": "flask-todo-gsi-name-dev"
            }
        })

    def test_resource_tags_applied(self):
        """Test that proper tags are applied to resources"""
        # Test DynamoDB table tags
        self.template.has_resource_properties("AWS::DynamoDB::Table", {
            "Tags": [
                {"Key": "Component", "Value": "database"},
                {"Key": "Environment", "Value": "dev"},
                {"Key": "Project", "Value": "flask-todo-cdk"}
            ]
        })

        # Test IAM role tags
        self.template.has_resource_properties("AWS::IAM::Role", {
            "Tags": [
                {"Key": "Component", "Value": "iam"},
                {"Key": "Environment", "Value": "dev"},
                {"Key": "Project", "Value": "flask-todo-cdk"}
            ]
        })

    def test_stack_properties_accessible(self):
        """Test that stack properties are accessible for cross-stack references"""
        assert hasattr(self.stack, 'table_name')
        assert hasattr(self.stack, 'table_arn')
        assert hasattr(self.stack, 'lambda_role_arn')
        assert self.stack.table_name == self.stack.todo_table.table_name
        assert self.stack.table_arn == self.stack.todo_table.table_arn
        assert self.stack.lambda_role_arn == self.stack.lambda_dynamodb_role.role_arn

    def test_resource_count(self):
        """Test that the expected number of resources are created"""
        # Should have: 1 DynamoDB table, 1 IAM role, 1 IAM policy, 1 CDK metadata
        self.template.resource_count_is("AWS::DynamoDB::Table", 1)
        self.template.resource_count_is("AWS::IAM::Role", 1)
        self.template.resource_count_is("AWS::IAM::Policy", 1)


if __name__ == "__main__":
    pytest.main([__file__])