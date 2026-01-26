from flask import request, jsonify
from app.routes import message_bp
from app.services.message_service import MessageService
from app.utils.decorators import handle_exceptions, require_auth, require_admin

message_service = MessageService()


@message_bp.route('', methods=['POST'])
@handle_exceptions
def create_message():
    """Create a new contact message (Public endpoint)"""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
    if not data.get('subject'):
        return jsonify({'error': 'Subject is required'}), 400
    if not data.get('message'):
        return jsonify({'error': 'Message is required'}), 400
    
    # Get user ID if logged in
    user_id = request.headers.get('X-User-Id')
    
    message = message_service.create_message(
        user_id=int(user_id) if user_id else None,
        email=data.get('email'),
        subject=data.get('subject'),
        message=data.get('message')
    )
    
    return jsonify({
        'message': 'Message sent successfully',
        'data': message.to_dict()
    }), 201


@message_bp.route('', methods=['GET'])
@handle_exceptions
@require_auth
@require_admin
def get_all_messages():
    """Get all messages (Admin only)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')  # 'open', 'closed', or None for all
    
    messages, total = message_service.get_all_messages(page, per_page, status)
    
    return jsonify({
        'messages': [m.to_dict() for m in messages],
        'total': total,
        'page': page,
        'perPage': per_page,
        'totalPages': (total + per_page - 1) // per_page
    }), 200


@message_bp.route('/<int:message_id>', methods=['GET'])
@handle_exceptions
@require_auth
@require_admin
def get_message(message_id):
    """Get a specific message (Admin only)"""
    message = message_service.get_message_by_id(message_id)
    
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    return jsonify({'message': message.to_dict()}), 200


@message_bp.route('/<int:message_id>/status', methods=['PUT'])
@handle_exceptions
@require_auth
@require_admin
def update_message_status(message_id):
    """Update message status (Admin only)"""
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['open', 'closed']:
        return jsonify({'error': 'Invalid status. Must be "open" or "closed"'}), 400
    
    message = message_service.update_status(message_id, new_status)
    
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    return jsonify({
        'message': 'Status updated successfully',
        'data': message.to_dict()
    }), 200
