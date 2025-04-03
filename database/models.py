
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, BigInteger
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
