"""
Fixtures for testing the Mashaaer application with pytest.
Provides test app, client, and database session fixtures.
"""

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask
from flask.testing import FlaskClient
from datetime import datetime, timedelta
from unittest.mock import patch

# Import your app factory and models
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.models import Base, Cache
import main  # Your main app file

@pytest.fixture(scope='session')
def app() -> Flask:
    """Creates a test Flask app instance."""
    # Store original DATABASE_URL
    original_db_url = os.environ.get('DATABASE_URL')
    
    # Set up an in-memory SQLite test database
    test_db_url = 'sqlite:///:memory:'
    os.environ['DATABASE_URL'] = test_db_url
    os.environ['TESTING'] = 'True'
    
    # Create the Flask app
    test_app = main.app
    test_app.config['TESTING'] = True
    test_app.config['SERVER_NAME'] = 'localhost'
    test_app.config['SQLALCHEMY_DATABASE_URI'] = test_db_url
    
    # Set up context
    with test_app.app_context():
        # Create engine and tables
        engine = create_engine(test_db_url)
        Base.metadata.create_all(engine)
        
        # Print tables for debugging
        table_names = Base.metadata.tables.keys()
        print(f"Created tables: {', '.join(table_names)}")
        
        yield test_app
        
        # Clean up
        Base.metadata.drop_all(engine)
    
    # Restore original DATABASE_URL
    if original_db_url:
        os.environ['DATABASE_URL'] = original_db_url
    else:
        os.environ.pop('DATABASE_URL', None)
    os.environ.pop('TESTING', None)

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """A Flask test client for making requests."""
    return app.test_client()

@pytest.fixture
def db_session(app: Flask):
    """A SQLAlchemy session for database interactions."""
    with app.app_context():
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        Base.metadata.create_all(engine)  # Ensure tables exist
        
        TestingSessionLocal = sessionmaker(bind=engine)
        session = TestingSessionLocal()
        
        try:
            yield session
        finally:
            session.rollback()  # Rollback any changes after the test
            session.close()

@pytest.fixture
def clear_cache(db_session):
    """Clears the cache table before each test."""
    def _clear_cache():
        db_session.query(Cache).delete()
        db_session.commit()
        # Log that cache has been cleared for debugging purposes
        print("Cache table cleared - all entries deleted and committed")
        # Verify the cache is empty
        count = db_session.query(Cache).count()
        print(f"Cache entries after clearing: {count}")
        if count > 0:
            print("WARNING: Cache was not properly cleared!")
    return _clear_cache

@pytest.fixture
def mock_emotion_tracker():
    """Mocks the emotion tracker for testing."""
    with patch('emotion_tracker.EmotionTracker.analyze_text') as mock:
        mock.return_value = {
            "primary_emotion": "happy",
            "emotions": {"happy": 0.8, "neutral": 0.2},
            "confidence": 0.8,
            "intensity": 0.8
        }
        yield mock

@pytest.fixture
def mock_tts_manager():
    """Mocks the TTS manager for testing."""
    with patch('tts.tts_manager.TTSManager.generate_tts') as mock:
        mock.return_value = "tts_cache/test_audio.mp3"
        yield mock

@pytest.fixture
def add_test_cache_entry(db_session):
    """Adds a test cache entry with a specific key."""
    def _add_entry(key, value, expiry_seconds=300):
        expires_at = datetime.now() + timedelta(seconds=expiry_seconds)
        cache_entry = Cache(
            key=key,
            value=value,
            expires_at=expires_at,
            content_type='application/json',
            hit_count=0
        )
        db_session.add(cache_entry)
        db_session.commit()
        return cache_entry
    
    return _add_entry