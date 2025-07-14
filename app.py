#!/usr/bin/env python3
"""
Flask Todo CDK Application Entry Point

This is the main CDK application that defines and synthesizes the infrastructure
for a serverless Flask-based todo application using AWS Lambda, API Gateway, and DynamoDB.
"""

import aws_cdk as cdk
from infrastructure.todo_stack import TodoStack

# Create CDK app instance
app = cdk.App()

# Development environment stack
TodoStack(app, "FlaskTodoCdkDev",
    env=cdk.Environment(
        account=app.node.try_get_context("account"),
        region=app.node.try_get_context("region") or "us-east-1"
    ),
    description="Flask Todo CDK Development Stack - Serverless todo app with Lambda, API Gateway, and DynamoDB"
)

# Production environment stack (commented out for now)
# TodoStack(app, "FlaskTodoCdkProd",
#     env=cdk.Environment(
#         account=app.node.try_get_context("prod_account"),
#         region=app.node.try_get_context("prod_region") or "us-east-1"
#     ),
#     description="Flask Todo CDK Production Stack"
# )

# Synthesize the CDK app
app.synth()