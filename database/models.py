
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, BigInteger, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Setting(Base):
    __tablename__ = 'settings'
    key = Column(String, primary_key=True)
    value = Column(Text)

class EmotionData(Base):
    __tablename__ = 'emotion_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String)
    emotion = Column(String)
    timestamp = Column(String)
    intensity = Column(Float)
    text = Column(Text)
    source = Column(String)
    context = Column(Text, nullable=True)  # Added context for emotion timeline

class Face(Base):
    __tablename__ = 'faces'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    image_path = Column(String)
    face_metadata = Column(Text)  # Renamed from metadata to avoid SQLAlchemy reserved word
    last_seen = Column(String)

class RecognitionHistory(Base):
    __tablename__ = 'recognition_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    timestamp = Column(String)
    confidence = Column(Float)
    emotion = Column(String)
    session_id = Column(String)

class VoiceLog(Base):
    __tablename__ = 'voice_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String)
    session_id = Column(String)
    language = Column(String)
    error_type = Column(String, nullable=True)
    raw_input = Column(Text, nullable=True)
    recognized_text = Column(Text, nullable=True)
    success = Column(Boolean, default=False)
    device_info = Column(Text, nullable=True)
    context = Column(String, nullable=True)

class UserProfile(Base):
    """User profile with subscription and preference information"""
    __tablename__ = 'user_profiles'
    user_id = Column(String, primary_key=True)
    username = Column(String, nullable=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, nullable=True)
    subscription_plan = Column(String, default='basic')  # 'basic', 'pro', 'supreme'
    subscription_expires = Column(DateTime, nullable=True)
    voice_personality = Column(String, default='classic-arabic')
    voice_speed = Column(Float, default=1.0)
    voice_pitch = Column(Float, default=1.0)
    preferred_language = Column(String, default='ar')
    last_intent = Column(String, nullable=True)
    is_offline_enabled = Column(Boolean, default=False)
    is_private_mode = Column(Boolean, default=False)

class SubscriptionHistory(Base):
    """History of subscription changes and billing"""
    __tablename__ = 'subscription_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String)  # Remove ForeignKey temporarily to fix DB initialization
    date = Column(DateTime, server_default=func.now())
    description = Column(String)
    amount = Column(Numeric(10, 2))
    status = Column(String)  # 'paid', 'pending', 'refunded'
    transaction_id = Column(String, nullable=True)

class Cache(Base):
    """
    Database-centric cache for storing computation-intensive operation results
    
    Advantages:
    - Persistence across application restarts
    - Shared cache across multiple instances
    - Automatic expiration management
    - Integration with existing database infrastructure
    """
    __tablename__ = 'response_cache'
    key = Column(String(255), primary_key=True, index=True)  # Index for faster lookups
    value = Column(Text)  # JSON serialized response data
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime)
    content_type = Column(String(50), default='application/json')  # For flexibility in caching different content types
    hit_count = Column(Integer, default=0)  # Track cache usage statistics
    last_hit_at = Column(DateTime, nullable=True)  # Track when the cache was last accessed
