from flask import Blueprint

message_bp = Blueprint('messages', __name__)

from app.routes.message_routes import *
