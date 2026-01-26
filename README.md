# Message Service

The Message Service is a microservice responsible for managing contact messages from users. It provides functionality for users to submit contact messages and for administrators to view and manage these messages.

## Features

- **Create Contact Messages**: Public endpoint for users to submit contact messages (logged in or anonymous)
- **View Messages**: Admin-only endpoint to retrieve all messages with pagination
- **Message Status Management**: Admin-only endpoint to update message status (open/closed)
- **Pagination Support**: Efficient message retrieval with pagination
- **Status Filtering**: Filter messages by status (open/closed)
- **Database Persistence**: MySQL database for message storage

## Tech Stack

- **Framework**: Flask 3.0.0
- **ORM**: Flask-SQLAlchemy 3.1.1
- **Database**: MySQL (via PyMySQL 1.1.0)
- **Authentication**: JWT token validation via headers
- **CORS**: Flask-Cors 4.0.0

## Project Structure

```
message-service/
├── app/
│   ├── __init__.py          # Flask app initialization
│   ├── config.py            # Configuration management
│   ├── models/
│   │   ├── __init__.py
│   │   └── message.py       # Message data model
│   ├── routes/
│   │   ├── __init__.py
│   │   └── message_routes.py # Message API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   └── message_service.py # Message business logic
│   └── utils/
│       ├── __init__.py
│       ├── decorators.py     # Decorators (auth, exception handling)
│       └── error_handlers.py # Error handlers
├── Dockerfile               # Docker image build file
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── README.md                # Project documentation
```

## Environment Variables

Create a `.env` file and set the following environment variables:

```env
# Flask settings
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Database settings
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/message_db

# JWT settings (for token validation)
JWT_SECRET=your-super-secret-jwt-key-change-in-production
```

## Installation and Running

### Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   Create a `.env` file and configure the required environment variables.

3. **Set Up Database**
   Ensure MySQL is running and create the database:
   ```sql
   CREATE DATABASE message_db;
   ```

4. **Run the Application**
   ```bash
   python run.py
   ```
   
   The service runs on `http://localhost:5004` by default.

### Using Docker

1. **Build Docker Image**
   ```bash
   docker build -t message-service .
   ```

2. **Run Container**
   ```bash
   docker run -p 5004:5004 --env-file .env message-service
   ```

## Database Schema

### Messages Table

| Column | Type | Description |
|--------|------|-------------|
| `message_id` | INTEGER | Primary key, auto-increment |
| `user_id` | INTEGER | User ID (nullable for anonymous messages) |
| `email` | VARCHAR(100) | Contact email address |
| `subject` | VARCHAR(200) | Message subject |
| `message` | TEXT | Message content |
| `date_created` | DATETIME | Timestamp of message creation |
| `status` | ENUM('open', 'closed') | Message status (default: 'open') |

## API Endpoints

### 1. Create Contact Message
**POST** `/messages`

Public endpoint - no authentication required.

Request Body:
```json
{
  "email": "user@example.com",
  "subject": "Question about the service",
  "message": "I have a question about..."
}
```

Optional Header (if user is logged in):
```
X-User-Id: 123
```

Success Response (201):
```json
{
  "message": "Message sent successfully",
  "data": {
    "messageId": 1,
    "userId": 123,
    "email": "user@example.com",
    "subject": "Question about the service",
    "message": "I have a question about...",
    "dateCreated": "2026-01-25T10:30:00",
    "status": "open"
  }
}
```

### 2. Get All Messages
**GET** `/messages`

Admin only - requires authentication and admin role.

Query Parameters:
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)
- `status` (optional): Filter by status ('open' or 'closed')

Request Headers:
```
Authorization: Bearer <token>
X-User-Id: 123
X-User-Type: admin
```

Success Response (200):
```json
{
  "messages": [
    {
      "messageId": 1,
      "userId": 123,
      "email": "user@example.com",
      "subject": "Question about the service",
      "message": "I have a question about...",
      "dateCreated": "2026-01-25T10:30:00",
      "status": "open"
    }
  ],
  "total": 50,
  "page": 1,
  "perPage": 20,
  "totalPages": 3
}
```

### 3. Get Message by ID
**GET** `/messages/{message_id}`

Admin only - requires authentication and admin role.

Request Headers:
```
Authorization: Bearer <token>
X-User-Id: 123
X-User-Type: admin
```

Success Response (200):
```json
{
  "message": {
    "messageId": 1,
    "userId": 123,
    "email": "user@example.com",
    "subject": "Question about the service",
    "message": "I have a question about...",
    "dateCreated": "2026-01-25T10:30:00",
    "status": "open"
  }
}
```

### 4. Update Message Status
**PUT** `/messages/{message_id}/status`

Admin only - requires authentication and admin role.

Request Headers:
```
Authorization: Bearer <token>
X-User-Id: 123
X-User-Type: admin
```

Request Body:
```json
{
  "status": "closed"
}
```

Success Response (200):
```json
{
  "message": "Status updated successfully",
  "data": {
    "messageId": 1,
    "userId": 123,
    "email": "user@example.com",
    "subject": "Question about the service",
    "message": "I have a question about...",
    "dateCreated": "2026-01-25T10:30:00",
    "status": "closed"
  }
}
```

### 5. Health Check
**GET** `/health`

Response:
```json
{
  "status": "healthy",
  "service": "message-service"
}
```

## Authentication

The service uses header-based authentication for protected endpoints:

- **X-User-Id**: User ID from JWT token (set by API gateway or auth middleware)
- **X-User-Type**: User type/role (must be 'admin' or 'super_admin' for admin endpoints)

The service expects these headers to be set by an API gateway or authentication middleware that validates JWT tokens.

## Authorization

- **Public Endpoints**: `/messages` (POST) - Anyone can create messages
- **Admin Endpoints**: All GET and PUT endpoints require admin or super_admin role

## Error Handling

The service handles the following errors:
- **400**: Bad Request (validation failures, invalid status values)
- **401**: Unauthorized (authentication required)
- **403**: Forbidden (admin access required)
- **404**: Not Found (message not found)
- **500**: Internal Server Error

## Message Status

Messages have two possible statuses:
- **open**: New or unprocessed message (default)
- **closed**: Message has been processed or resolved

## Development Guide

### Code Structure
- **models/**: Database models using SQLAlchemy
- **routes/**: API endpoint definitions
- **services/**: Business logic
- **utils/**: Utility functions (decorators, error handlers)

### Database Migrations

The application automatically creates tables on startup using `db.create_all()`. For production, consider using Flask-Migrate for proper database migrations.

### Logging

The application uses Python's `logging` module to record logs. Log levels and formats can be configured in `run.py`.

### Testing

To run tests:
```bash
# If test files exist
pytest
```

## Security Considerations

1. **Input Validation**: All required fields are validated before processing
2. **SQL Injection**: SQLAlchemy ORM prevents SQL injection attacks
3. **Authentication**: Admin endpoints require proper authentication headers
4. **CORS**: Configured to allow all origins in development. Restrict in production.

## Database Connection

The service uses SQLAlchemy with connection pooling:
- `pool_recycle`: 300 seconds
- `pool_pre_ping`: Enabled for connection health checks

Ensure your MySQL server is configured to handle the expected connection load.

## License

Refer to the `LICENSE` file for license information.
