"""
Tests for the TodoStack

This module contains tests for the main infrastructure stack.
"""

import aws_cdk as cdk
import aws_cdk.assertions as assertions
from infrastructure.todo_stack import TodoStack


def test_todo_stack_creates_database_resources():
    """Test that the TodoStack creates the database resources."""
    # ARRANGE
    app = cdk.App()
    
    # ACT
    stack = TodoStack(app, "TestTodoStack")
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


def test_todo_stack_dev_environment():
    """Test that the TodoStack creates the expected resources in dev environment."""
    # ARRANGE
    app = cdk.App()
    
    # ACT
    stack = TodoStack(app, "TestTodoStackDev")
    template = assertions.Template.from_stack(stack)
    
    # ASSERT
    # Check that the table has the correct properties for development
    template.has_resource_properties("AWS::DynamoDB::Table", {
        "BillingMode": "PAY_PER_REQUEST"
    })


def test_todo_stack_prod_environment():
    """Test that the TodoStack creates the expected resources in prod environment."""
    # ARRANGE
    app = cdk.App()
    
    # ACT
    stack = TodoStack(app, "TestTodoStackProd")
    template = assertions.Template.from_stack(stack)
    
    # ASSERT
    # Check that the table has the correct properties for production
    template.has_resource_properties("AWS::DynamoDB::Table", {
        "BillingMode": "PROVISIONED",
        "ProvisionedThroughput": {
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5
        }
    })


def test_todo_stack_outputs():
    """Test that the TodoStack exports the expected outputs."""
    # ARRANGE
    app = cdk.App()
    
    # ACT
    stack = TodoStack(app, "TestTodoStack")
    template = assertions.Template.from_stack(stack)
    
    # ASSERT
    # Check that the stack status output is created
    template.has_output("StackStatus", {
        "Value": "DynamoDB infrastructure implemented - ready for Flask API implementation"
    })