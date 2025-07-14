# Flask Todo CDK

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![AWS CDK v2](https://img.shields.io/badge/AWS%20CDK-v2-orange)](https://docs.aws.amazon.com/cdk/v2/guide/home.html)

A serverless Flask Todo web application using AWS CDK with Lambda, API Gateway, and DynamoDB. This project demonstrates how to build a complete serverless web application using AWS CDK for infrastructure as code.

## 📋 Project Overview

This project implements a serverless Todo application with:

- **Frontend**: Simple HTML/CSS/JS interface
- **Backend**: Python Flask API deployed as AWS Lambda
- **Database**: Amazon DynamoDB
- **Infrastructure**: AWS CDK for defining all cloud resources

## 🚀 Getting Started

### Prerequisites

- [Python 3.9+](https://www.python.org/downloads/)
- [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate credentials
- [AWS CDK v2](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html)
- [Node.js and npm](https://nodejs.org/) (required for CDK)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/flask-todo-cdk.git
   cd flask-todo-cdk
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

4. Bootstrap CDK (if you haven't already):
   ```bash
   cdk bootstrap
   ```

5. Deploy the application:
   ```bash
   cdk deploy
   ```

## 🏗️ Project Structure

```
flask-todo-cdk/
├── app.py                 # CDK app entry point
├── requirements.txt       # CDK dependencies
├── requirements-dev.txt   # Development dependencies
├── cdk.json              # CDK configuration
├── lambda/               # Lambda function code
│   └── todo_api/         # Flask application
├── infrastructure/       # CDK stacks
├── tests/               # Unit tests
├── scripts/             # Deployment scripts
├── .gitignore           # Git ignore file
└── README.md            # Project documentation
```

## 🧪 Development

### Local Testing

To run tests:
```bash
pytest
```

### Code Quality

Format code with Black:
```bash
black .
```

Lint code with Flake8:
```bash
flake8
```

Type checking with MyPy:
```bash
mypy .
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
