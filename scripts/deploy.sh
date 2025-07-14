#!/bin/bash
# Deployment script for Flask Todo CDK application

# Exit on error
set -e

echo "Starting deployment of Flask Todo CDK application..."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
# Install dependencies
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Skipping dependency installation."
fi

# Deploy with CDK
echo "Deploying with CDK..."

# Deploy with CDK
echo "Deploying with CDK..."
cdk deploy --require-approval never

echo "Deployment completed successfully!"