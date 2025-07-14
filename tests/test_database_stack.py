"""
Tests for the DynamoDB Database Stack

This module contains tests for the DatabaseStack class to ensure it meets
the requirements specified in Issue #2.
"""

import aws_cdk as cdk
import pytest
from aws_cdk.assertions import Template, Match
from infrastructure.database_stack import DatabaseStack


def test_dynamodb_table_created():
    """Test that the DynamoDB table is created with the correct properties"""
    # GIVEN
    app = cdk.App()
    
    # WHEN
    stack = DatabaseStack(app, "TestDatabaseStack")
    template = Template.from_stack(stack)
    
    # THEN
    template.resource_count_is("AWS::DynamoDB::Table", 1)


def test_dynamodb_table_dev_configuration():
    """Test that the DynamoDB table has the correct development configuration"""
    # GIVEN
    app = cdk.App()
    
    # WHEN
    stack = DatabaseStack(app, "TestDatabaseStack", is_production=False)
    template = Template.from_stack(stack)
    
    # THEN
    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        {
            "TableName": "flask-todo-table-dev",
            "BillingMode": "PAY_PER_REQUEST",
            "PointInTimeRecoverySpecification": {"PointInTimeRecoveryEnabled": True},
            "KeySchema": [
                {"AttributeName": "todo_id", "KeyType": "HASH"}
            ],
            "AttributeDefinitions": Match.array_with([
                {"AttributeName": "todo_id", "AttributeType": "S"},
                {"AttributeName": "status", "AttributeType": "S"},
                {"AttributeName": "created_at", "AttributeType": "S"}
            ])
        }
    )


def test_dynamodb_table_prod_configuration():
    """Test that the DynamoDB table has the correct production configuration"""
    # GIVEN
    app = cdk.App()
    
    # WHEN
    stack = DatabaseStack(app, "TestDatabaseStack", is_production=True)
    template = Template.from_stack(stack)
    
    # THEN
    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        {
            "TableName": "flask-todo-table-prod",
            "BillingMode": "PROVISIONED",
            "ProvisionedThroughput": {
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            },
            "PointInTimeRecoverySpecification": {"PointInTimeRecoveryEnabled": True}
        }
    )


def test_gsi_created():
    """Test that the GSI is created with the correct configuration"""
    # GIVEN
    app = cdk.App()
    
    # WHEN
    stack = DatabaseStack(app, "TestDatabaseStack")
    template = Template.from_stack(stack)
    
    # THEN
    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        {
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "StatusDateIndex",
                    "KeySchema": [
                        {"AttributeName": "status", "KeyType": "HASH"},
                        {"AttributeName": "created_at", "KeyType": "RANGE"}
                    ],
                    "Projection": {"ProjectionType": "ALL"}
                }
            ]
        }
    )


def test_outputs_created():
    """Test that the stack outputs are created correctly"""
    # GIVEN
    app = cdk.App()
    
    # WHEN
    stack = DatabaseStack(app, "TestDatabaseStack", is_production=False)
    template = Template.from_stack(stack)
    
    # THEN
    template.has_output("TodoTableName", {
        "Export": {"Name": "TodoTable-dev-Name"}
    })
    
    template.has_output("TodoTableArn", {
        "Export": {"Name": "TodoTable-dev-Arn"}
    })