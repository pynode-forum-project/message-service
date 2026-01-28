from datetime import datetime, timezone
from app import db


class Message(db.Model):
    """Message model for contact admin functionality"""
    
    __tablename__ = 'messages'
    
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=True)  # Can be null for non-logged in users
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    status = db.Column(db.Enum('open', 'closed'), default='open', index=True)
    
    def __repr__(self):
        return f'<Message {self.message_id}>'
    
    def to_dict(self):
        """Convert message to dictionary"""
        date_created = self.date_created
        if date_created:
            # Normalize to UTC with explicit offset so clients parse correctly.
            if date_created.tzinfo is None:
                date_created = date_created.replace(tzinfo=timezone.utc)
            date_created = date_created.isoformat()
        return {
            'messageId': self.message_id,
            'userId': self.user_id,
            'email': self.email,
            'subject': self.subject,
            'message': self.message,
            'dateCreated': date_created if date_created else None,
            'status': self.status
        }
