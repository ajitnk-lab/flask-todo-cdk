from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/api/todos', methods=['GET'])
def get_todos():
    """Placeholder endpoint to get all todos."""
    return jsonify({
        'todos': [
            {'id': '1', 'title': 'Learn AWS CDK', 'completed': False},
            {'id': '2', 'title': 'Build Flask API', 'completed': False},
            {'id': '3', 'title': 'Deploy to AWS', 'completed': False}
        ]
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})


def handler(event, context):
    """Lambda handler function."""
    # This will be implemented in a future issue
    # to integrate with API Gateway
    return {
        'statusCode': 200,
        'body': 'Flask Todo API - Coming Soon!'
    }


if __name__ == '__main__':
    app.run(debug=True)