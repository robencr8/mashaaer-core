#!/usr/bin/env python3
"""
Test fixtures and configuration for the Mashaaer Feelings test suite.
"""

import os
import sys
import pytest
from flask import Flask

# Add project root to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import application modules
from database.db_manager import DatabaseManager
from emotion_tracker import EmotionTracker
from config import Config


@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["DEBUG"] = True
    app.config["SERVER_NAME"] = "localhost"
    
    # Create test instance URL context
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def mock_db_manager():
    """Create a mock database manager for testing."""
    class MockDatabaseManager:
        def __init__(self):
            self.queries = []
            self.data = {
                "emotions": [],
                "profiles": [],
                "sessions": [],
                "conversations": []
            }
        
        def execute_query(self, query, params=None, fetch=False):
            self.queries.append((query, params))
            return []
            
        def insert_emotion(self, session_id, text, emotion_data):
            self.data["emotions"].append({
                "session_id": session_id,
                "text": text,
                "emotion_data": emotion_data
            })
            return True
            
        def get_emotion_history(self, session_id=None, limit=10):
            return self.data["emotions"][:limit]
            
        def create_user_profile(self, profile_data):
            self.data["profiles"].append(profile_data)
            return True
            
        def get_user_profile(self, profile_id=None):
            if not self.data["profiles"]:
                return None
            return self.data["profiles"][0]
            
        def create_session(self):
            session_id = f"test_session_{len(self.data['sessions'])}"
            self.data["sessions"].append({"id": session_id})
            return session_id
            
        def log_conversation(self, session_id, user_input, response, emotion=None):
            self.data["conversations"].append({
                "session_id": session_id,
                "user_input": user_input,
                "response": response,
                "emotion": emotion
            })
            return True
        
        def get_recent_conversations(self, session_id, limit=5):
            return [c for c in self.data["conversations"] 
                   if c["session_id"] == session_id][:limit]
            
    return MockDatabaseManager()


@pytest.fixture
def mock_emotion_tracker(mock_db_manager):
    """Create a mock emotion tracker for testing."""
    class MockEmotionTracker:
        def __init__(self, db_manager):
            self.db_manager = db_manager
            
        def analyze_text(self, text, context=None):
            # Return mock emotion analysis
            if "happy" in text.lower() or "joy" in text.lower():
                emotion = {
                    "primary": "joy",
                    "secondary": "surprise",
                    "scores": {
                        "joy": 0.8,
                        "surprise": 0.4,
                        "sadness": 0.1,
                        "anger": 0.0,
                        "fear": 0.0,
                        "neutral": 0.2
                    },
                    "intensity": 0.8,
                    "confidence": 0.9
                }
            elif "sad" in text.lower() or "upset" in text.lower():
                emotion = {
                    "primary": "sadness",
                    "secondary": "neutral",
                    "scores": {
                        "joy": 0.1,
                        "surprise": 0.0,
                        "sadness": 0.7,
                        "anger": 0.2,
                        "fear": 0.1,
                        "neutral": 0.3
                    },
                    "intensity": 0.7,
                    "confidence": 0.8
                }
            else:
                emotion = {
                    "primary": "neutral",
                    "secondary": None,
                    "scores": {
                        "joy": 0.2,
                        "surprise": 0.1,
                        "sadness": 0.1,
                        "anger": 0.1,
                        "fear": 0.1,
                        "neutral": 0.6
                    },
                    "intensity": 0.3,
                    "confidence": 0.7
                }
            
            return emotion
            
        def log_emotion(self, session_id, text, emotion_data):
            return self.db_manager.insert_emotion(session_id, text, emotion_data)
            
        def get_emotion_history(self, session_id=None, limit=10):
            return self.db_manager.get_emotion_history(session_id, limit)
            
    return MockEmotionTracker(mock_db_manager)


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    class MockConfig:
        def __init__(self):
            # Default test configuration
            self.config = {
                "APP_NAME": "Mashaaer Test",
                "DEBUG": True,
                "TESTING": True,
                "OFFLINE_MODE": False,
                "DEFAULT_LANGUAGE": "en",
                "SMS_ENABLED": True,
                "VOICE_ENABLED": True,
                "FACE_RECOGNITION_ENABLED": True,
                "EMOTION_ANALYSIS_ENABLED": True,
                "AUTO_LEARNING_ENABLED": False,
                "DEFAULT_TTS_PROVIDER": "mock_tts",
                "DEFAULT_STT_PROVIDER": "mock_stt",
                "DEFAULT_AI_MODEL": "mock_model"
            }
            
        def get(self, key, default=None):
            return self.config.get(key, default)
            
        def set(self, key, value):
            self.config[key] = value
            
        def is_offline(self):
            return self.config.get("OFFLINE_MODE", False)
            
    return MockConfig()