#!/usr/bin/env python3
"""
Tests for the emotion tracker module.
"""

import pytest

from emotion_tracker import EmotionTracker

class TestEmotionTracker:
    """Test suite for the EmotionTracker class."""
    
    def test_init(self, mock_db_manager):
        """Test initialization of the EmotionTracker."""
        tracker = EmotionTracker(mock_db_manager)
        assert tracker is not None
        assert tracker.db_manager == mock_db_manager
    
    def test_analyze_text_happy(self, mock_db_manager):
        """Test emotion analysis on happy text."""
        tracker = EmotionTracker(mock_db_manager)
        
        # Mock the analyze_text method
        def mock_analyze_text(text, context=None):
            return {
                "primary": "joy",
                "secondary": "surprise",
                "scores": {
                    "joy": 0.8,
                    "surprise": 0.5,
                    "sadness": 0.1,
                    "anger": 0.0,
                    "fear": 0.0,
                    "neutral": 0.1
                },
                "intensity": 0.8,
                "confidence": 0.9
            }
        
        # Replace the actual method with our mock
        tracker._analyze_with_model = mock_analyze_text
        
        # Test with happy text
        result = tracker.analyze_text("I am so happy today!")
        
        assert result["primary"] == "joy"
        assert result["scores"]["joy"] > 0.5
    
    def test_analyze_text_sad(self, mock_db_manager):
        """Test emotion analysis on sad text."""
        tracker = EmotionTracker(mock_db_manager)
        
        # Mock the analyze_text method
        def mock_analyze_text(text, context=None):
            return {
                "primary": "sadness",
                "secondary": "neutral",
                "scores": {
                    "joy": 0.1,
                    "surprise": 0.0,
                    "sadness": 0.7,
                    "anger": 0.1,
                    "fear": 0.1,
                    "neutral": 0.3
                },
                "intensity": 0.7,
                "confidence": 0.8
            }
        

def test_analyze_with_rules_synonyms(emotion_tracker):
    text = "I am joyful and gleeful today."
    assert emotion_tracker._analyze_with_rules(text) == "happy"

def test_analyze_with_rules_contextual(emotion_tracker):
    text = "I can't be happier about the new updates."
    context = ["These updates really made my day"]
    assert emotion_tracker.analyze_text(text, context) == "happy"

        # Replace the actual method with our mock
        tracker._analyze_with_model = mock_analyze_text
        
        # Test with sad text
        result = tracker.analyze_text("I feel so sad and upset.")
        
        assert result["primary"] == "sadness"
        assert result["scores"]["sadness"] > 0.5
    
    def test_analyze_text_neutral(self, mock_db_manager):
        """Test emotion analysis on neutral text."""
        tracker = EmotionTracker(mock_db_manager)
        
        # Mock the analyze_text method
        def mock_analyze_text(text, context=None):
            return {
                "primary": "neutral",
                "secondary": None,
                "scores": {
                    "joy": 0.2,
                    "surprise": 0.1,
                    "sadness": 0.1,
                    "anger": 0.1,
                    "fear": 0.0,
                    "neutral": 0.7
                },
                "intensity": 0.3,
                "confidence": 0.8
            }
        

def test_analyze_with_rules_synonyms(emotion_tracker):
    text = "I am joyful and gleeful today."
    assert emotion_tracker._analyze_with_rules(text) == "happy"

def test_analyze_with_rules_contextual(emotion_tracker):
    text = "I can't be happier about the new updates."
    context = ["These updates really made my day"]
    assert emotion_tracker.analyze_text(text, context) == "happy"

        # Replace the actual method with our mock
        tracker._analyze_with_model = mock_analyze_text
        
        # Test with neutral text
        result = tracker.analyze_text("The sky is blue today.")
        
        assert result["primary"] == "neutral"
        assert result["scores"]["neutral"] > 0.5
    
    def test_analyze_text_empty(self, mock_db_manager):
        """Test emotion analysis on empty text."""
        tracker = EmotionTracker(mock_db_manager)
        
        # Test with empty text
        result = tracker.analyze_text("")
        
        # Empty text should return a default neutral emotion
        assert result["primary"] == "neutral"
    
    def test_log_emotion(self, mock_db_manager):
        """Test logging an emotion to the database."""
        tracker = EmotionTracker(mock_db_manager)
        session_id = "test_session_123"
        text = "I am happy today"
        emotion_data = {
            "primary": "joy",
            "secondary": "surprise",
            "scores": {
                "joy": 0.8,
                "surprise": 0.5,
                "sadness": 0.1,
                "anger": 0.0,
                "fear": 0.0,
                "neutral": 0.1
            }
        }
        
        # Call the log_emotion method
        result = tracker.log_emotion(session_id, text, emotion_data)
        
        # Check that the insert_emotion method was called
        assert result is True
        assert len(mock_db_manager.data["emotions"]) == 1
        assert mock_db_manager.data["emotions"][0]["session_id"] == session_id
        assert mock_db_manager.data["emotions"][0]["text"] == text
    
    def test_get_emotion_history(self, mock_db_manager):
        """Test retrieving emotion history from the database."""
        tracker = EmotionTracker(mock_db_manager)
        session_id = "test_session_123"
        
        # Add some test emotions
        mock_db_manager.data["emotions"] = [
            {
                "session_id": session_id,
                "text": "I am happy",
                "emotion_data": {"primary": "joy"}
            },
            {
                "session_id": session_id,
                "text": "I am sad",
                "emotion_data": {"primary": "sadness"}
            },
            {
                "session_id": "other_session",
                "text": "I am angry",
                "emotion_data": {"primary": "anger"}
            }
        ]
        
        # Get emotion history for the session
        history = tracker.get_emotion_history(session_id, 10)
        
        # Check that only emotions for the session are returned
        assert len(history) == 2
        assert all(item["session_id"] == session_id for item in history)