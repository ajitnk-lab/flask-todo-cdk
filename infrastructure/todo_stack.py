from aws_cdk import Stack
from constructs import Construct


class TodoStack(Stack):
    """
    CDK Stack for the Flask Todo application.
    This stack will contain all the resources needed for the Todo application.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        # In future issues, we will add:
        # - DynamoDB Table
        # - Lambda Function
        # - API Gateway
        # - IAM Roles and Policies