"""
Tests for the Todo Stack

This module contains tests for the TodoStack class to ensure it correctly
integrates with the DatabaseStack.
"""

import aws_cdk as cdk
import pytest
from aws_cdk.assertions import Template, Match
from infrastructure.todo_stack import TodoStack


def test_database_stack_integrated():
    """Test that the DatabaseStack is integrated into the TodoStack"""
    # GIVEN
    app = cdk.App()
    
    # WHEN
    stack = TodoStack(app, "TestTodoStack")
    template = Template.from_stack(stack)
    
    # THEN
    # Verify that the DynamoDB table is created
    template.resource_count_is("AWS::DynamoDB::Table", 1)
    
    # Verify that the table has the correct properties
    template.has_resource_properties(
        "AWS::DynamoDB::Table",
        {
            "KeySchema": [
                {"AttributeName": "todo_id", "KeyType": "HASH"}
            ],
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


def test_stack_outputs():
    """Test that the stack outputs are created correctly"""
    # GIVEN
    app = cdk.App()
    
    # WHEN
    stack = TodoStack(app, "TestTodoStack")
    template = Template.from_stack(stack)
    
    # THEN
    # Verify that the stack status output is updated
    template.has_output("StackStatus", {
        "Value": "DynamoDB table created - ready for Lambda implementation"
    })
    
    # Verify that the table outputs are created
    template.has_output("DatabaseStackTodoTableName", {})
    template.has_output("DatabaseStackTodoTableArn", {})