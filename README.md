# Message Service

Message Service is a Flask-based microservice that handles contact us functionality for the Forum Project. It stores and retrieves messages from users.

## Tech Stack

- **Framework**: Flask 3.0
- **ORM**: Flask-SQLAlchemy
- **Database**: MySQL 8.0
- **Authentication**: Flask-JWT-Extended

## Project Structure

```
message-service/
├── app/
│   ├── __init__.py              # Flask application factory
│   ├── config.py                # Configuration (database, JWT, etc.)
│   ├── models/
│   │   ├── __init__.py          # SQLAlchemy db instance
│   │   └── message.py           # Message model
│   └── routes/
│       ├── __init__.py
│       └── message_routes.py   # Message endpoints
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── README.md
```

## API Endpoints

### POST /api/messages

Send a new message (contact us).

**Request:**
```json
{
  "email": "user@example.com",
  "message": "Your message here",
  "userId": "optional-user-id",
  "images": ["url1", "url2"],
  "attachments": ["url1", "url2"],
  "status": "pending"
}
```

**Response (Success - 201):**
```json
{
  "message": "Message sent successfully",
  "data": {
    "messageId": "uuid",
    "userId": "user-id",
    "email": "user@example.com",
    "message": "Your message here",
    "dateCreated": "2024-01-01T00:00:00",
    "status": "pending",
    "images": ["url1", "url2"],
    "attachments": ["url1", "url2"]
  }
}
```

### GET /api/messages

Get inbox messages (Admin only).

**Query Parameters:**
- `page` (default: 1)
- `per_page` (default: 20, max: 100)
- `status` (optional: filter by status)

**Response (Success - 200):**
```json
{
  "messages": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

## Database Schema

### Message Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| messageId | VARCHAR(36) | PRIMARY KEY | UUID, auto-generated |
| userId | VARCHAR(36) | NULLABLE | User ID if logged in |
| email | VARCHAR(100) | NOT NULL | Sender's email |
| message | TEXT | NOT NULL | Message content |
| dateCreated | DATETIME | NOT NULL | Creation timestamp |
| status | VARCHAR(50) | NOT NULL, DEFAULT 'pending' | Message status |
| images | TEXT | NULLABLE | JSON array of image URLs |
| attachments | TEXT | NULLABLE | JSON array of attachment URLs |

## Usage

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export DATABASE_URI=mysql+pymysql://root:root@localhost:3306/forum_message_db
export JWT_SECRET=your-secret-key
```

3. Run the service:
```bash
python run.py
```

The service will run on `http://0.0.0.0:5004`
