import os 
from datetime import timedelta

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        'mysql+pymysql://root:root@localhost:3306/forum_message_db'
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv('JWT_SECRET', 'your-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=3)
    
    JWT_IDENTITY_CLAIM = 'user_id'
    JWT_ALGORITHM = 'HS256'
