"""
Tests for the DatabaseStack

This module contains tests for the DynamoDB infrastructure stack.
"""

import aws_cdk as cdk
import aws_cdk.assertions as assertions
from infrastructure.database_stack import DatabaseStack


def test_database_stack_dev_environment():
    """Test that the DatabaseStack creates the expected resources in dev environment."""
    # ARRANGE
    app = cdk.App()
    
    # ACT
    stack = DatabaseStack(app, "TestDatabaseStack", is_prod=False)
    template = assertions.Template.from_stack(stack)
    
    # ASSERT
    # Check that the DynamoDB table is created
    template.resource_count_is("AWS::DynamoDB::Table", 1)
    
    # Check that the table has the correct properties
    template.has_resource_properties("AWS::DynamoDB::Table", {
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
        ],
        "BillingMode": "PAY_PER_REQUEST",
        "PointInTimeRecoverySpecification": {
            "PointInTimeRecoveryEnabled": True
        },
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


def test_database_stack_prod_environment():
    """Test that the DatabaseStack creates the expected resources in prod environment."""
    # ARRANGE
    app = cdk.App()
    
    # ACT
    stack = DatabaseStack(app, "TestDatabaseStack", is_prod=True)
    template = assertions.Template.from_stack(stack)
    
    # ASSERT
    # Check that the DynamoDB table is created
    template.resource_count_is("AWS::DynamoDB::Table", 1)
    
    # Check that the table has the correct properties for production
    template.has_resource_properties("AWS::DynamoDB::Table", {
        "BillingMode": "PROVISIONED",
        "ProvisionedThroughput": {
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5
        },
        "PointInTimeRecoverySpecification": {
            "PointInTimeRecoveryEnabled": True
        }
    })


def test_database_stack_outputs():
    """Test that the DatabaseStack exports the expected outputs."""
    # ARRANGE
    app = cdk.App()
    
    # ACT
    stack = DatabaseStack(app, "TestDatabaseStack")
    template = assertions.Template.from_stack(stack)
    
    # ASSERT
    # Check that the outputs are created
    template.has_output("TodoTableName", {})
    template.has_output("TodoTableArn", {})