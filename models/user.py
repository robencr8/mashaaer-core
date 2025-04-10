"""
User model for Mashaaer Feelings Application
"""

import datetime
from flask_login import UserMixin
from sqlalchemy.sql import func

from main import db

class User(UserMixin, db.Model):
    """User model for authentication and profile"""
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    
    # Profile information
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    language_preference = db.Column(db.String(10), default='en')  # en or ar
    
    # Avatar/profile information
    avatar = db.Column(db.String(256))  # URL or emoji
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # User preferences
    notification_enabled = db.Column(db.Boolean, default=True)
    daily_reminder_time = db.Column(db.Time)
    
    # Relationships will be added by the emotional progress models
    # emotion_progress - relationship to UserEmotionProgress
    # achievements - relationship to UserAchievement
    # learning_path_progress - relationship to UserLearningPathProgress
    
    def __repr__(self):
        return f'<User {self.username}>'