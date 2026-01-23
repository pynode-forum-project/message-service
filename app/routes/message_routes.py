from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models import db
from app.models.message import Message
from datetime import datetime

message_bp = Blueprint('messages', __name__)

def is_admin(jwt_claims):
    user_type = jwt_claims.get('user_type', 'user').lower()
    return user_type in ['admin', 'superadmin', 'super_admin']

@message_bp.route('', methods=['POST'])
def send_message():
    """
    Expected: JSON with 'email', 'message', optional 'userId', 'images', 'attachments'
    Returns: JSON with created message
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Request body is required'}), 400
    
    errors = {}
    
    if 'email' not in data or not data['email']:
        errors['email'] = 'Email is required'
    elif len(data['email']) > 100:
        errors['email'] = 'Email must be at most 100 characters'
    
    if 'message' not in data or not data['message']:
        errors['message'] = 'Message is required'
    
    if errors:
        return jsonify({
            'message': 'Validation failed',
            'details': errors
        }), 400
    
    try:
        message = Message(
            userId=data.get('userId'),
            email=data['email'],
            message=data['message'],
            status='pending'
        )
        
        if 'images' in data:
            message.set_images(data['images'])
        
        if 'attachments' in data:
            message.set_attachments(data['attachments'])
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'message': 'Message sent successfully',
            'data': message.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': 'Failed to send message',
            'error': str(e)
        }), 500

@message_bp.route('', methods=['GET'])
@jwt_required()
def get_messages():
    """
    Expected: Query params: page, per_page, status (optional)
    Returns: JSON with messages list and pagination
    """
    jwt_claims = get_jwt()
    current_user_id = get_jwt_identity()
    
    if not is_admin(jwt_claims):
        return jsonify({'message': 'Admin access required'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status_filter = request.args.get('status', type=str)
    
    per_page = min(per_page, 100)
    
    query = Message.query
    
    if status_filter:
        query = query.filter(Message.status == status_filter)
    
    query = query.order_by(Message.dateCreated.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    messages = [msg.to_dict() for msg in pagination.items]
    
    return jsonify({
        'messages': messages,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200
