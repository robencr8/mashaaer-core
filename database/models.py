
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, BigInteger, DateTime
from sqlalchemy.sql import func
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
