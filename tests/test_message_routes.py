"""
API Integration Tests for Message Service Routes

Tests the HTTP endpoints using Flask test client:
- POST /messages
- GET /messages
- GET /messages/{id}
- PUT /messages/{id}/status
- GET /health
"""

import pytest
from unittest.mock import patch, MagicMock
from app import create_app, db
from app.models.message import Message


@pytest.fixture
def app():
    """Create Flask app for testing with in-memory SQLite database"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET'] = 'test-jwt-secret-key'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def sample_message(app):
    """Create a sample message in the test database"""
    with app.app_context():
        message = Message(
            user_id=1,
            email='test@example.com',
            subject='Test Subject',
            message='Test message content',
            status='open'
        )
        db.session.add(message)
        db.session.commit()
        # Extract message_id before session closes to avoid DetachedInstanceError
        message_id = message.message_id
        db.session.expunge(message)  # Detach from session
        return type('obj', (object,), {'message_id': message_id})()


def create_auth_headers(user_id=1, user_type='admin'):
    """Helper to create authentication headers"""
    return {
        'X-User-Id': str(user_id),
        'X-User-Type': user_type,
        'Authorization': 'Bearer test-token'
    }


class TestCreateMessageEndpoint:
    """Test POST /messages endpoint"""
    
    def test_create_message_success(self, client, app):
        """Test successful message creation returns 201"""
        with app.app_context():
            response = client.post('/messages', json={
                'email': 'user@example.com',
                'subject': 'Test Subject',
                'message': 'Test message content'
            })
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['message'] == 'Message sent successfully'
            assert 'data' in data
            assert data['data']['email'] == 'user@example.com'
            assert data['data']['subject'] == 'Test Subject'
    
    def test_create_message_with_user_id(self, client, app):
        """Test message creation with logged-in user"""
        with app.app_context():
            response = client.post('/messages', json={
                'email': 'user@example.com',
                'subject': 'Test Subject',
                'message': 'Test message content'
            }, headers={
                'X-User-Id': '123'
            })
            
            assert response.status_code == 201
            data = response.get_json()
            assert data['data']['userId'] == 123
    
    def test_create_message_missing_email(self, client):
        """Test message creation without email returns 400"""
        response = client.post('/messages', json={
            'subject': 'Test Subject',
            'message': 'Test message content'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'email' in data['error'].lower()
    
    def test_create_message_missing_subject(self, client):
        """Test message creation without subject returns 400"""
        response = client.post('/messages', json={
            'email': 'user@example.com',
            'message': 'Test message content'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'subject' in data['error'].lower()
    
    def test_create_message_missing_message(self, client):
        """Test message creation without message content returns 400"""
        response = client.post('/messages', json={
            'email': 'user@example.com',
            'subject': 'Test Subject'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'message' in data['error'].lower()


class TestGetAllMessagesEndpoint:
    """Test GET /messages endpoint"""
    
    def test_get_all_messages_success(self, client, app, sample_message):
        """Test successful retrieval of all messages returns 200"""
        with app.app_context():
            # Create another message
            message2 = Message(
                user_id=2,
                email='user2@example.com',
                subject='Subject 2',
                message='Message 2',
                status='open'
            )
            db.session.add(message2)
            db.session.commit()
            
            response = client.get('/messages', headers=create_auth_headers())
            
            assert response.status_code == 200
            data = response.get_json()
            assert 'messages' in data
            assert len(data['messages']) == 2
            assert 'total' in data
            assert 'page' in data
            assert 'perPage' in data
            assert 'totalPages' in data
    
    def test_get_all_messages_pagination(self, client, app):
        """Test pagination works correctly"""
        with app.app_context():
            # Create multiple messages
            for i in range(25):
                message = Message(
                    user_id=i,
                    email=f'user{i}@example.com',
                    subject=f'Subject {i}',
                    message=f'Message {i}',
                    status='open'
                )
                db.session.add(message)
            db.session.commit()
            
            response = client.get('/messages?page=1&per_page=10', headers=create_auth_headers())
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['messages']) == 10
            assert data['total'] == 25
            assert data['page'] == 1
            assert data['perPage'] == 10
    
    def test_get_all_messages_filter_by_status(self, client, app):
        """Test filtering messages by status"""
        with app.app_context():
            # Create open and closed messages
            open_msg = Message(
                user_id=1,
                email='open@example.com',
                subject='Open',
                message='Open message',
                status='open'
            )
            closed_msg = Message(
                user_id=2,
                email='closed@example.com',
                subject='Closed',
                message='Closed message',
                status='closed'
            )
            db.session.add(open_msg)
            db.session.add(closed_msg)
            db.session.commit()
            
            response = client.get('/messages?status=open', headers=create_auth_headers())
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['messages']) == 1
            assert data['messages'][0]['status'] == 'open'
    
    def test_get_all_messages_requires_auth(self, client):
        """Test that getting messages requires authentication"""
        response = client.get('/messages')
        
        assert response.status_code == 401
    
    def test_get_all_messages_requires_admin(self, client):
        """Test that getting messages requires admin role"""
        response = client.get('/messages', headers={
            'X-User-Id': '1',
            'X-User-Type': 'user',  # Not admin
            'Authorization': 'Bearer test-token'
        })
        
        assert response.status_code == 403


class TestGetMessageEndpoint:
    """Test GET /messages/{id} endpoint"""
    
    def test_get_message_success(self, client, app, sample_message):
        """Test successful retrieval of a message returns 200"""
        with app.app_context():
            response = client.get(f'/messages/{sample_message.message_id}', headers=create_auth_headers())
            
            assert response.status_code == 200
            data = response.get_json()
            assert 'message' in data
            assert data['message']['messageId'] == sample_message.message_id
            assert data['message']['email'] == 'test@example.com'
    
    def test_get_message_not_found(self, client, app):
        """Test getting non-existent message returns 404"""
        with app.app_context():
            response = client.get('/messages/99999', headers=create_auth_headers())
            
            assert response.status_code == 404
            data = response.get_json()
            assert 'error' in data
    
    def test_get_message_requires_auth(self, client, app, sample_message):
        """Test that getting a message requires authentication"""
        with app.app_context():
            response = client.get(f'/messages/{sample_message.message_id}')
            
            assert response.status_code == 401
    
    def test_get_message_requires_admin(self, client, app, sample_message):
        """Test that getting a message requires admin role"""
        with app.app_context():
            response = client.get(f'/messages/{sample_message.message_id}', headers={
                'X-User-Id': '1',
                'X-User-Type': 'user',  # Not admin
                'Authorization': 'Bearer test-token'
            })
            
            assert response.status_code == 403


class TestUpdateMessageStatusEndpoint:
    """Test PUT /messages/{id}/status endpoint"""
    
    def test_update_status_success(self, client, app, sample_message):
        """Test successful status update returns 200"""
        with app.app_context():
            # Verify initial status by querying the database
            initial_message = Message.query.get(sample_message.message_id)
            assert initial_message.status == 'open'
            
            response = client.put(
                f'/messages/{sample_message.message_id}/status',
                json={'status': 'closed'},
                headers=create_auth_headers()
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['message'] == 'Status updated successfully'
            assert data['data']['status'] == 'closed'
            
            # Verify in database
            updated_message = Message.query.get(sample_message.message_id)
            assert updated_message.status == 'closed'
    
    def test_update_status_invalid_status(self, client, app, sample_message):
        """Test updating with invalid status returns 400"""
        with app.app_context():
            response = client.put(
                f'/messages/{sample_message.message_id}/status',
                json={'status': 'invalid'},
                headers=create_auth_headers()
            )
            
            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
    
    def test_update_status_not_found(self, client, app):
        """Test updating non-existent message returns 404"""
        with app.app_context():
            response = client.put(
                '/messages/99999/status',
                json={'status': 'closed'},
                headers=create_auth_headers()
            )
            
            assert response.status_code == 404
            data = response.get_json()
            assert 'error' in data
    
    def test_update_status_requires_auth(self, client, app, sample_message):
        """Test that updating status requires authentication"""
        with app.app_context():
            response = client.put(
                f'/messages/{sample_message.message_id}/status',
                json={'status': 'closed'}
            )
            
            assert response.status_code == 401
    
    def test_update_status_requires_admin(self, client, app, sample_message):
        """Test that updating status requires admin role"""
        with app.app_context():
            response = client.put(
                f'/messages/{sample_message.message_id}/status',
                json={'status': 'closed'},
                headers={
                    'X-User-Id': '1',
                    'X-User-Type': 'user',  # Not admin
                    'Authorization': 'Bearer test-token'
                }
            )
            
            assert response.status_code == 403


class TestHealthEndpoint:
    """Test GET /health endpoint"""
    
    def test_health_check(self, client):
        """Test health endpoint returns 200"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'message-service'
