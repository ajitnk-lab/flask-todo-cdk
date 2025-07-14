# Flask Todo CDK

[![CDK Version](https://img.shields.io/badge/CDK-2.100.0+-blue.svg)](https://github.com/aws/aws-cdk)
[![Python Version](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Development Status](https://img.shields.io/badge/Status-In%20Development-orange.svg)](https://github.com/ajitnk-lab/flask-todo-cdk/issues)

A serverless Flask-based todo web application built with AWS CDK, featuring Lambda functions, API Gateway, and DynamoDB. This project demonstrates modern serverless architecture patterns and infrastructure as code best practices.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │───▶│  Lambda (Flask) │───▶│    DynamoDB     │
│                 │    │                 │    │                 │
│ REST API        │    │ Python 3.11     │    │ Todo Storage    │
│ CORS Enabled    │    │ Flask App       │    │ NoSQL Database  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Features

- **Serverless Architecture**: Built on AWS Lambda for automatic scaling and cost efficiency
- **RESTful API**: Complete CRUD operations for todo management
- **Infrastructure as Code**: Fully defined using AWS CDK (Python)
- **Modern Python**: Flask application with Python 3.11+
- **NoSQL Database**: DynamoDB for high-performance data storage
- **Development Workflow**: GitHub Issues-driven development with Amazon Q Developer

## 📋 Development Status

This project is being developed incrementally through a series of GitHub Issues, each assigned to Amazon Q Developer:

### 🎯 Issue Series Progress

- ✅ **Issue #1**: Project Foundation (COMPLETED)
- ✅ **Issue #2**: DynamoDB Infrastructure (COMPLETED)
- ⏳ **Issue #3**: Flask Application Core  
- ⏳ **Issue #4**: Lambda Infrastructure
- ⏳ **Issue #5**: API Gateway Integration
- ⏳ **Issue #6**: Testing and Validation
- ⏳ **Issue #7**: Deployment and Documentation

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+**: [Download Python](https://www.python.org/downloads/)
- **Node.js 18+**: Required for AWS CDK CLI
- **AWS CLI**: [Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **AWS CDK CLI**: Install with `npm install -g aws-cdk`
- **Git**: For version control

### AWS Configuration

Configure your AWS credentials:

```bash
aws configure
```

Or set environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/ajitnk-lab/flask-todo-cdk.git
cd flask-todo-cdk
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. CDK Bootstrap (First Time Only)

```bash
cdk bootstrap
```

### 4. Synthesize CDK Stack

```bash
cdk synth
```

### 5. Deploy (When Ready)

```bash
cdk deploy
```

## 📁 Project Structure

```
flask-todo-cdk/
├── app.py                      # CDK application entry point
├── requirements.txt            # CDK dependencies
├── requirements-dev.txt        # Development dependencies
├── cdk.json                   # CDK configuration
├── .gitignore                 # Git ignore patterns
├── README.md                  # This file
├── infrastructure/            # CDK stack definitions
│   ├── __init__.py
│   ├── todo_stack.py         # Main infrastructure stack
│   └── database_stack.py     # DynamoDB stack (Issue #2)
├── lambda/                   # Lambda function code
│   └── todo_api/            # Flask application
│       ├── __init__.py
│       ├── app.py           # Flask app (Issue #3)
│       ├── models.py        # Data models (Issue #3)
│       └── requirements.txt # Lambda dependencies
├── tests/                   # Unit and integration tests
│   └── __init__.py
└── scripts/                 # Deployment and utility scripts
    └── deploy.sh           # Deployment script (Issue #7)
```

## 🔧 Development Workflow

This project follows a GitHub Issues-driven development approach:

1. **Issue Creation**: Each feature/component is defined as a GitHub Issue
2. **Amazon Q Developer**: Issues are assigned to Amazon Q Developer for implementation
3. **Incremental Development**: Each issue builds upon the previous foundation
4. **Testing**: Comprehensive testing at each stage
5. **Documentation**: Continuous documentation updates

### Current Implementation Status

#### ✅ Completed (Issue #1)
- [x] CDK project structure
- [x] Basic configuration files
- [x] Package structure and placeholders
- [x] Development environment setup
- [x] Git repository initialization

#### ✅ Completed (Issue #2)
- [x] DynamoDB table implementation with partition key
- [x] Global Secondary Index for status-based queries
- [x] Environment-specific configurations (dev/prod)
- [x] IAM permissions for Lambda access
- [x] Table outputs for cross-stack references

#### 🔄 In Progress
- [ ] Flask application core (Issue #3)
- [ ] Lambda function setup (Issue #4)
- [ ] API Gateway configuration (Issue #5)
- [ ] Testing suite (Issue #6)
- [ ] Deployment automation (Issue #7)

## 🧪 Testing

Run tests using pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_stack.py
```

## 📚 API Documentation

The Flask Todo API will provide the following endpoints (implemented in Issue #3):

- `GET /todos` - List all todos
- `POST /todos` - Create a new todo
- `GET /todos/{id}` - Get a specific todo
- `PUT /todos/{id}` - Update a todo
- `DELETE /todos/{id}` - Delete a todo

## 🗄️ Database Schema

The DynamoDB table has the following schema:

### Todo Table
- **Table Name**: `flask-todo-table-{env}` (where env is 'dev' or 'prod')
- **Partition Key**: `todo_id` (String)
- **Attributes**:
  - `todo_id`: String (Primary Key)
  - `title`: String (Required)
  - `description`: String (Optional)
  - `status`: String (Required) - Values: "pending", "completed", "archived"
  - `created_at`: String (ISO 8601 timestamp)
  - `updated_at`: String (ISO 8601 timestamp)
  - `user_id`: String (Future use for multi-user support)

### Global Secondary Index (GSI)
- **GSI Name**: `StatusDateIndex`
- **Partition Key**: `status` (String)
- **Sort Key**: `created_at` (String)
- **Purpose**: Query todos by status and sort by creation date

### Environment-Specific Configurations
- **Development**:
  - Pay-per-request billing
  - DESTROY removal policy
  - Point-in-time recovery enabled
  - AWS managed encryption
- **Production**:
  - Provisioned billing (5 RCU/WCU)
  - RETAIN removal policy
  - Point-in-time recovery enabled
  - AWS managed encryption

## 🔍 Monitoring and Logging

- **CloudWatch Logs**: Automatic logging for Lambda functions
- **CloudWatch Metrics**: Performance and usage metrics
- **X-Ray Tracing**: Distributed tracing (optional)

## 🤝 Contributing

This project uses an automated development workflow with Amazon Q Developer. To contribute:

1. Review open GitHub Issues
2. Follow the established issue-driven development pattern
3. Ensure all tests pass
4. Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/ajitnk-lab/flask-todo-cdk/issues)
- **AWS CDK Documentation**: [CDK Developer Guide](https://docs.aws.amazon.com/cdk/)
- **Flask Documentation**: [Flask User Guide](https://flask.palletsprojects.com/)

## 🏷️ Tags

`aws-cdk` `flask` `serverless` `lambda` `api-gateway` `dynamodb` `python` `infrastructure-as-code` `amazon-q-developer`

---

**Built with ❤️ using AWS CDK and automated development workflows**