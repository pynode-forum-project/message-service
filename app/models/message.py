from app.models import db
from datetime import datetime
import uuid
import json

class Message(db.Model):
    __tablename__ = 'messages'

    messageId = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    userId = db.Column(db.String(36), nullable=True)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    dateCreated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False, default='pending')
    images = db.Column(db.Text, nullable=True)
    attachments = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Message {self.messageId}>'

    def set_images(self, images_list):
        """Set images as JSON string"""
        if images_list:
            self.images = json.dumps(images_list)
        else:
            self.images = None

    def get_images(self):
        """Get images as list"""
        if self.images:
            try:
                return json.loads(self.images)
            except:
                return []
        return []

    def set_attachments(self, attachments_list):
        """Set attachments as JSON string"""
        if attachments_list:
            self.attachments = json.dumps(attachments_list)
        else:
            self.attachments = None

    def get_attachments(self):
        """Get attachments as list"""
        if self.attachments:
            try:
                return json.loads(self.attachments)
            except:
                return []
        return []

    def to_dict(self):
        return {
            'messageId': self.messageId,
            'userId': self.userId,
            'email': self.email,
            'message': self.message,
            'dateCreated': self.dateCreated.isoformat() if self.dateCreated else None,
            'status': self.status,
            'images': self.get_images(),
            'attachments': self.get_attachments()
        }
