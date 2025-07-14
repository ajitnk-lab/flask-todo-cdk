# Flask Todo API

This directory contains the Flask application that provides REST API endpoints for todo operations. It integrates with DynamoDB for CRUD operations on todo items.

## API Endpoints

### Health Check
```
GET /health
```
Returns the health status of the API and its connection to the database.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2023-05-15T12:34:56.789012",
  "database": "connected",
  "table": "flask-todo-dev"
}
```

### List Todos
```
GET /todos
```
Returns a list of all todos with optional status filtering and pagination.

**Query Parameters:**
- `status` - Filter by status (pending, completed, archived)
- `limit` - Maximum number of items to return (default: 50, max: 100)
- `next_token` - Token for pagination

**Response:**
```json
{
  "todos": [
    {
      "todo_id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Complete project",
      "description": "Finish the todo API implementation",
      "status": "pending",
      "created_at": "2023-05-15T12:34:56.789012",
      "updated_at": "2023-05-15T12:34:56.789012"
    }
  ],
  "count": 1,
  "total_scanned": 1,
  "next_token": "eyJsYXN0X2V2YWx1YXRlZF9rZXkiOnsia2V5IjoidmFsdWUifX0="
}
```

### Get Todo
```
GET /todos/{todo_id}
```
Returns a specific todo by ID.

**Response:**
```json
{
  "todo_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Complete project",
  "description": "Finish the todo API implementation",
  "status": "pending",
  "created_at": "2023-05-15T12:34:56.789012",
  "updated_at": "2023-05-15T12:34:56.789012"
}
```

### Create Todo
```
POST /todos
```
Creates a new todo.

**Request Body:**
```json
{
  "title": "Complete project",
  "description": "Finish the todo API implementation",
  "status": "pending"
}
```

**Response:**
```json
{
  "todo_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Complete project",
  "description": "Finish the todo API implementation",
  "status": "pending",
  "created_at": "2023-05-15T12:34:56.789012",
  "updated_at": "2023-05-15T12:34:56.789012"
}
```

### Update Todo
```
PUT /todos/{todo_id}
```
Updates an existing todo.

**Request Body:**
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "status": "completed"
}
```

**Response:**
```json
{
  "todo_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Updated title",
  "description": "Updated description",
  "status": "completed",
  "created_at": "2023-05-15T12:34:56.789012",
  "updated_at": "2023-05-15T13:45:56.789012"
}
```

### Delete Todo
```
DELETE /todos/{todo_id}
```
Deletes a todo.

**Response:**
```json
{
  "message": "Todo 123e4567-e89b-12d3-a456-426614174000 deleted successfully"
}
```

## Data Model

```python
Todo Model:
{
    "todo_id": "string (UUID)",
    "title": "string (required, max 200 chars)",
    "description": "string (optional, max 1000 chars)",
    "status": "string (pending|completed|archived)",
    "created_at": "string (ISO 8601)",
    "updated_at": "string (ISO 8601)"
}
```

## Error Handling

All endpoints return appropriate HTTP status codes and error messages:

- `400 Bad Request` - Invalid input data
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server-side error

Error response format:
```json
{
  "error": "Error message",
  "details": "Additional error details (optional)"
}
```

## Local Development

To run the API locally:

```bash
export FLASK_APP=lambda/todo_api/todo_api.py
export FLASK_ENV=development
export TODO_TABLE_NAME=flask-todo-dev
flask run
```

## Testing

Run the tests with pytest:

```bash
pytest tests/test_todo_api.py
```