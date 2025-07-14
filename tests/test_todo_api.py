"""
Unit tests for Todo API

Tests the Flask application endpoints and functionality.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime
import uuid

# Import the Flask app
from lambda.todo_api.todo_api import app
from lambda.todo_api.models import TodoModel


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestTodoAPI:
    """Test suite for Todo API endpoints."""

    @patch('lambda.todo_api.todo_api.db')
    def test_health_check_success(self, mock_db, client):
        """Test health check endpoint when database is connected."""
        # Mock the database connection check
        mock_db.check_connection.return_value = True
        mock_db.table_name = "test-table"

        # Make request to health check endpoint
        response = client.get('/health')
        data = json.loads(response.data)

        # Assert response
        assert response.status_code == 200
        assert data['status'] == 'healthy'
        assert data['database'] == 'connected'
        assert data['table'] == 'test-table'
        assert 'timestamp' in data

    @patch('lambda.todo_api.todo_api.db')
    def test_health_check_failure(self, mock_db, client):
        """Test health check endpoint when database is disconnected."""
        # Mock the database connection check
        mock_db.check_connection.return_value = False
        mock_db.table_name = "test-table"

        # Make request to health check endpoint
        response = client.get('/health')
        data = json.loads(response.data)

        # Assert response
        assert response.status_code == 500
        assert data['status'] == 'unhealthy'
        assert data['database'] == 'disconnected'
        assert 'timestamp' in data

    @patch('lambda.todo_api.todo_api.db')
    def test_list_todos_success(self, mock_db, client):
        """Test listing todos."""
        # Mock the database response
        mock_todos = [
            {
                'todo_id': str(uuid.uuid4()),
                'title': 'Test Todo 1',
                'description': 'Test Description 1',
                'status': 'pending',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            },
            {
                'todo_id': str(uuid.uuid4()),
                'title': 'Test Todo 2',
                'description': 'Test Description 2',
                'status': 'completed',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
        ]
        mock_db.list_todos.return_value = {
            'todos': mock_todos,
            'count': len(mock_todos),
            'total_scanned': len(mock_todos)
        }

        # Make request to list todos endpoint
        response = client.get('/todos')
        data = json.loads(response.data)

        # Assert response
        assert response.status_code == 200
        assert len(data['todos']) == 2
        assert data['count'] == 2
        assert data['total_scanned'] == 2
        assert mock_db.list_todos.called

    @patch('lambda.todo_api.todo_api.db')
    def test_list_todos_with_status_filter(self, mock_db, client):
        """Test listing todos with status filter."""
        # Mock the database response
        mock_todos = [
            {
                'todo_id': str(uuid.uuid4()),
                'title': 'Test Todo 1',
                'description': 'Test Description 1',
                'status': 'completed',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
        ]
        mock_db.list_todos.return_value = {
            'todos': mock_todos,
            'count': len(mock_todos),
            'total_scanned': len(mock_todos)
        }

        # Make request to list todos endpoint with status filter
        response = client.get('/todos?status=completed')
        data = json.loads(response.data)

        # Assert response
        assert response.status_code == 200
        assert len(data['todos']) == 1
        assert data['todos'][0]['status'] == 'completed'
        mock_db.list_todos.assert_called_with(status='completed', limit=50, next_token=None)

    @patch('lambda.todo_api.todo_api.db')
    def test_get_todo_success(self, mock_db, client):
        """Test getting a specific todo."""
        # Create a mock todo
        todo_id = str(uuid.uuid4())
        mock_todo = {
            'todo_id': todo_id,
            'title': 'Test Todo',
            'description': 'Test Description',
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        mock_db.get_todo.return_value = mock_todo

        # Make request to get todo endpoint
        response = client.get(f'/todos/{todo_id}')
        data = json.loads(response.data)

        # Assert response
        assert response.status_code == 200
        assert data['todo_id'] == todo_id
        assert data['title'] == 'Test Todo'
        assert data['status'] == 'pending'
        mock_db.get_todo.assert_called_with(todo_id)

    @patch('lambda.todo_api.todo_api.db')
    def test_get_todo_not_found(self, mock_db, client):
        """Test getting a non-existent todo."""
        # Mock the database response for a non-existent todo
        mock_db.get_todo.return_value = None

        # Make request to get todo endpoint
        response = client.get('/todos/non-existent-id')
        data = json.loads(response.data)

        # Assert response
        assert response.status_code == 404
        assert 'error' in data
        assert data['error'] == 'Todo not found'

    @patch('lambda.todo_api.todo_api.db')
    @patch('lambda.todo_api.models.TodoModel.from_dict')
    def test_create_todo_success(self, mock_from_dict, mock_db, client):
        """Test creating a new todo."""
        # Create a mock todo
        todo_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        mock_todo = {
            'todo_id': todo_id,
            'title': 'New Todo',
            'description': 'New Description',
            'status': 'pending',
            'created_at': timestamp,
            'updated_at': timestamp
        }
        mock_from_dict.return_value = mock_todo
        mock_db.create_todo.return_value = mock_todo

        # Make request to create todo endpoint
        response = client.post(
            '/todos',
            data=json.dumps({
                'title': 'New Todo',
                'description': 'New Description'
            }),
            content_type='application/json'
        )
        data = json.loads(response.data)

        # Assert response
        assert response.status_code == 201
        assert data['todo_id'] == todo_id
        assert data['title'] == 'New Todo'
        assert data['status'] == 'pending'
        assert mock_db.create_todo.called

    @patch('lambda.todo_api.todo_api.db')
    def test_create_todo_invalid_data(self, mock_db, client):
        """Test creating a todo with invalid data."""
        # Make request to create todo endpoint with invalid data
        response = client.post(
            '/todos',
            data=json.dumps({}),  # Missing required title
            content_type='application/json'
        )
        data = json.loads(response.data)

        # Assert response
        assert response.status_code == 400
        assert 'error' in data
        assert data['error'] == 'Title is required'
        assert not mock_db.create_todo.called

    @patch('lambda.todo_api.todo_api.db')
    def test_update_todo_success(self, mock_db, client):
        """Test updating a todo."""
        # Create a mock todo
        todo_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        mock_todo = {
            'todo_id': todo_id,
            'title': 'Original Todo',
            'description': 'Original Description',
            'status': 'pending',
            'created_at': timestamp,
            'updated_at': timestamp
        }
        mock_updated_todo = {
            'todo_id': todo_id,
            'title': 'Updated Todo',
            'description': 'Updated Description',
            'status': 'completed',
            'created_at': timestamp,
            'updated_at': datetime.utcnow().isoformat()
        }
        mock_db.get_todo.return_value = mock_todo
        mock_db.update_todo.return_value = mock_updated_todo

        # Make request to update todo endpoint
        response = client.put(
            f'/todos/{todo_id}',
            data=json.dumps({
                'title': 'Updated Todo',
                'description': 'Updated Description',
                'status': 'completed'
            }),
            content_type='application/json'
        )
        data = json.loads(response.data)

        # Assert response
        assert response.status_code == 200
        assert data['todo_id'] == todo_id
        assert data['title'] == 'Updated Todo'
        assert data['description'] == 'Updated Description'
        assert data['status'] == 'completed'
        assert mock_db.update_todo.called

    @patch('lambda.todo_api.todo_api.db')
    def test_update_todo_not_found(self, mock_db, client):
        """Test updating a non-existent todo."""
        # Mock the database response for a non-existent todo
        mock_db.get_todo.return_value = None

        # Make request to update todo endpoint
        response = client.put(
            '/todos/non-existent-id',
            data=json.dumps({
                'title': 'Updated Todo'
            }),
            content_type='application/json'
        )
        data = json.loads(response.data)

        # Assert response
        assert response.status_code == 404
        assert 'error' in data
        assert data['error'] == 'Todo not found'
        assert not mock_db.update_todo.called

    @patch('lambda.todo_api.todo_api.db')
    def test_delete_todo_success(self, mock_db, client):
        """Test deleting a todo."""
        # Create a mock todo
        todo_id = str(uuid.uuid4())
        mock_todo = {
            'todo_id': todo_id,
            'title': 'Test Todo',
            'description': 'Test Description',
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        mock_db.get_todo.return_value = mock_todo
        mock_db.delete_todo.return_value = True

        # Make request to delete todo endpoint
        response = client.delete(f'/todos/{todo_id}')
        data = json.loads(response.data)

        # Assert response
        assert response.status_code == 200
        assert 'message' in data
        assert f'Todo {todo_id} deleted successfully' in data['message']
        mock_db.delete_todo.assert_called_with(todo_id)

    @patch('lambda.todo_api.todo_api.db')
    def test_delete_todo_not_found(self, mock_db, client):
        """Test deleting a non-existent todo."""
        # Mock the database response for a non-existent todo
        mock_db.get_todo.return_value = None

        # Make request to delete todo endpoint
        response = client.delete('/todos/non-existent-id')
        data = json.loads(response.data)

        # Assert response
        assert response.status_code == 404
        assert 'error' in data
        assert data['error'] == 'Todo not found'
        assert not mock_db.delete_todo.called


if __name__ == "__main__":
    pytest.main([__file__])