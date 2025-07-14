import aws_cdk as cdk
import pytest
from infrastructure.todo_stack import TodoStack


def test_todo_stack_creation():
    """Test that the TodoStack can be instantiated."""
    # GIVEN
    app = cdk.App()
    
    # WHEN
    stack = TodoStack(app, "TestStack")
    
    # THEN
    # This test simply verifies that the stack can be instantiated without errors
    assert stack is not None
    assert stack.stack_name == "TestStack"