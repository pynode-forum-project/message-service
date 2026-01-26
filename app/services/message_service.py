from app import db
from app.models.message import Message


class MessageService:
    """Service for message operations"""
    
    def create_message(self, user_id: int, email: str, subject: str, message: str) -> Message:
        """Create a new contact message"""
        msg = Message(
            user_id=user_id,
            email=email,
            subject=subject,
            message=message
        )
        
        db.session.add(msg)
        db.session.commit()
        
        return msg
    
    def get_all_messages(self, page: int = 1, per_page: int = 20, status: str = None):
        """Get all messages with pagination and optional status filter"""
        query = Message.query
        
        if status:
            query = query.filter_by(status=status)
        
        pagination = query.order_by(Message.date_created.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return pagination.items, pagination.total
    
    def get_message_by_id(self, message_id: int) -> Message:
        """Get message by ID"""
        return Message.query.get(message_id)
    
    def update_status(self, message_id: int, status: str) -> Message:
        """Update message status"""
        message = self.get_message_by_id(message_id)
        
        if not message:
            return None
        
        message.status = status
        db.session.commit()
        
        return message
