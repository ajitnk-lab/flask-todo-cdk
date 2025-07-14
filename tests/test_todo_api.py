"""
Unit and Integration Tests for Flask Todo API

Tests all API endpoints, error handling, validation, and DynamoDB integration.
"""

import pytest
import json
import uuid
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

# Add lambda directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda'))

from todo_api import app, validate_todo_data, create_todo_item, TodoValidationError


class TestTodoAPI:
    """Test suite for Flask Todo API"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    @pytest.fixture
    def sample_todo(self):
        """Sample todo data for testing"""
        return {
            'title': 'Test Todo',
            'description': 'This is a test todo item',
            'status': 'pending'
        }

    @pytest.fixture
    def mock_table(self):
        """Mock DynamoDB table"""
        with patch('todo_api.table') as mock:
            yield mock

    def test_health_check_success(self, client, mock_table):
        """Test health check endpoint - success"""
        mock_table.table_status = 'ACTIVE'
        
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'table' in data

    def test_health_check_failure(self, client, mock_table):
        """Test health check endpoint - failure"""
        mock_table.table_status.side_effect = Exception("Connection failed")
        
        response = client.get('/health')
        assert response.status_code == 503
        
        data = json.loads(response.data)
        assert data['status'] == 'unhealthy'

    def test_list_todos_empty(self, client, mock_table):
        """Test listing todos when table is empty"""
        mock_table.scan.return_value = {'Items': []}
        
        response = client.get('/todos')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['todos'] == []
        assert data['count'] == 0

    def test_list_todos_with_data(self, client, mock_table):
        """Test listing todos with data"""
        sample_todos = [
            {
                'todo_id': '1',
                'title': 'Todo 1',
                'status': 'pending',
                'created_at': '2023-01-01T00:00:00Z'
            },
            {
                'todo_id': '2',
                'title': 'Todo 2',
                'status': 'completed',
                'created_at': '2023-01-02T00:00:00Z'
            }
        ]
        mock_table.scan.return_value = {'Items': sample_todos}
        
        response = client.get('/todos')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['todos']) == 2
        assert data['count'] == 2

    def test_list_todos_with_status_filter(self, client, mock_table):
        """Test listing todos with status filter"""
        sample_todos = [
            {
                'todo_id': '1',
                'title': 'Completed Todo',
                'status': 'completed',
                'created_at': '2023-01-01T00:00:00Z'
            }
        ]
        mock_table.query.return_value = {'Items': sample_todos}
        
        response = client.get('/todos?status=completed')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['todos']) == 1
        assert data['status_filter'] == 'completed'
        mock_table.query.assert_called_once()

    def test_get_todo_success(self, client, mock_table):
        """Test getting a specific todo - success"""
        todo_id = str(uuid.uuid4())
        sample_todo = {
            'todo_id': todo_id,
            'title': 'Test Todo',
            'description': 'Test description',
            'status': 'pending'
        }
        mock_table.get_item.return_value = {'Item': sample_todo}
        
        response = client.get(f'/todos/{todo_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['todo_id'] == todo_id
        assert data['title'] == 'Test Todo'

    def test_get_todo_not_found(self, client, mock_table):
        """Test getting a non-existent todo"""
        todo_id = str(uuid.uuid4())
        mock_table.get_item.return_value = {}
        
        response = client.get(f'/todos/{todo_id}')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data

    def test_create_todo_success(self, client, mock_table, sample_todo):
        """Test creating a new todo - success"""
        mock_table.put_item.return_value = {}
        
        response = client.post('/todos',
                             data=json.dumps(sample_todo),
                             content_type='application/json')
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert data['title'] == sample_todo['title']
        assert data['description'] == sample_todo['description']
        assert data['status'] == sample_todo['status']
        assert 'todo_id' in data
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_create_todo_invalid_json(self, client):
        """Test creating todo with invalid JSON"""
        response = client.post('/todos',
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code == 400

    def test_create_todo_missing_content_type(self, client, sample_todo):
        """Test creating todo without JSON content type"""
        response = client.post('/todos', data=json.dumps(sample_todo))
        assert response.status_code == 400

    def test_create_todo_missing_title(self, client, mock_table):
        """Test creating todo without title"""
        invalid_todo = {'description': 'No title', 'status': 'pending'}
        
        response = client.post('/todos',
                             data=json.dumps(invalid_todo),
                             content_type='application/json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'Title is required' in data['error']

    def test_create_todo_invalid_status(self, client, mock_table):
        """Test creating todo with invalid status"""
        invalid_todo = {
            'title': 'Test Todo',
            'description': 'Test description',
            'status': 'invalid_status'
        }
        
        response = client.post('/todos',
                             data=json.dumps(invalid_todo),
                             content_type='application/json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'Status must be one of' in data['error']

    def test_update_todo_success(self, client, mock_table, sample_todo):
        """Test updating an existing todo - success"""
        todo_id = str(uuid.uuid4())
        existing_todo = {
            'todo_id': todo_id,
            'title': 'Old Title',
            'created_at': '2023-01-01T00:00:00Z'
        }
        mock_table.get_item.return_value = {'Item': existing_todo}
        mock_table.put_item.return_value = {}
        
        updated_data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'status': 'completed'
        }
        
        response = client.put(f'/todos/{todo_id}',
                            data=json.dumps(updated_data),
                            content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['title'] == 'Updated Title'
        assert data['status'] == 'completed'
        assert data['created_at'] == existing_todo['created_at']

    def test_update_todo_not_found(self, client, mock_table, sample_todo):
        """Test updating a non-existent todo"""
        todo_id = str(uuid.uuid4())
        mock_table.get_item.return_value = {}
        
        response = client.put(f'/todos/{todo_id}',
                            data=json.dumps(sample_todo),
                            content_type='application/json')
        assert response.status_code == 404

    def test_delete_todo_success(self, client, mock_table):
        """Test deleting an existing todo - success"""
        todo_id = str(uuid.uuid4())
        existing_todo = {'todo_id': todo_id, 'title': 'Test Todo'}
        mock_table.get_item.return_value = {'Item': existing_todo}
        mock_table.delete_item.return_value = {}
        
        response = client.delete(f'/todos/{todo_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'deleted successfully' in data['message']

    def test_delete_todo_not_found(self, client, mock_table):
        """Test deleting a non-existent todo"""
        todo_id = str(uuid.uuid4())
        mock_table.get_item.return_value = {}
        
        response = client.delete(f'/todos/{todo_id}')
        assert response.status_code == 404

    def test_invalid_endpoint(self, client):
        """Test accessing invalid endpoint"""
        response = client.get('/invalid-endpoint')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'not found' in data['error'].lower()

    def test_method_not_allowed(self, client):
        """Test using invalid HTTP method"""
        response = client.patch('/todos')
        assert response.status_code == 405


class TestValidation:
    """Test suite for data validation functions"""

    def test_validate_todo_data_success(self):
        """Test successful validation"""
        valid_data = {
            'title': 'Test Todo',
            'description': 'Test description',
            'status': 'pending'
        }
        
        result = validate_todo_data(valid_data)
        assert result['title'] == 'Test Todo'
        assert result['description'] == 'Test description'
        assert result['status'] == 'pending'

    def test_validate_todo_data_minimal(self):
        """Test validation with minimal data"""
        minimal_data = {'title': 'Test Todo'}
        
        result = validate_todo_data(minimal_data)
        assert result['title'] == 'Test Todo'
        assert result['description'] == ''
        assert result['status'] == 'pending'

    def test_validate_todo_data_empty_title(self):
        """Test validation with empty title"""
        invalid_data = {'title': '   ', 'description': 'Test'}
        
        with pytest.raises(TodoValidationError, match="Title is required"):
            validate_todo_data(invalid_data)

    def test_validate_todo_data_long_title(self):
        """Test validation with title too long"""
        invalid_data = {'title': 'x' * 201}
        
        with pytest.raises(TodoValidationError, match="Title must be"):
            validate_todo_data(invalid_data)

    def test_validate_todo_data_long_description(self):
        """Test validation with description too long"""
        invalid_data = {
            'title': 'Test Todo',
            'description': 'x' * 1001
        }
        
        with pytest.raises(TodoValidationError, match="Description must be"):
            validate_todo_data(invalid_data)

    def test_validate_todo_data_invalid_status(self):
        """Test validation with invalid status"""
        invalid_data = {
            'title': 'Test Todo',
            'status': 'invalid'
        }
        
        with pytest.raises(TodoValidationError, match="Status must be one of"):
            validate_todo_data(invalid_data)

    def test_validate_todo_data_not_dict(self):
        """Test validation with non-dictionary input"""
        with pytest.raises(TodoValidationError, match="must be a JSON object"):
            validate_todo_data("not a dict")

    def test_create_todo_item(self):
        """Test todo item creation"""
        todo_id = str(uuid.uuid4())
        validated_data = {
            'title': 'Test Todo',
            'description': 'Test description',
            'status': 'pending'
        }
        
        result = create_todo_item(todo_id, validated_data)
        
        assert result['todo_id'] == todo_id
        assert result['title'] == 'Test Todo'
        assert result['description'] == 'Test description'
        assert result['status'] == 'pending'
        assert 'created_at' in result
        assert 'updated_at' in result
        assert result['created_at'] == result['updated_at']


if __name__ == '__main__':
    pytest.main([__file__])