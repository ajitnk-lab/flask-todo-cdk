#!/usr/bin/env python3
import aws_cdk as cdk
from infrastructure.todo_stack import TodoStack

app = cdk.App()

# Development environment
TodoStack(app, "FlaskTodoCdkDev",
    env=cdk.Environment(
        account=app.node.try_get_context("account"),
        region=app.node.try_get_context("region") or "us-east-1"
    )
)

app.synth()