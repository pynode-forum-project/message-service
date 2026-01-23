import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config
from app.models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    JWTManager(app)

    with app.app_context():
        db.create_all()

    from app.routes.message_routes import message_bp
    app.register_blueprint(message_bp, url_prefix='/api/messages')
    
    return app
