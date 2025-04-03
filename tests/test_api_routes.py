#!/usr/bin/env python3
"""
Tests for the API routes module.
"""

import json
import os
import pytest

from api_routes import init_api

# Mock setup function
@pytest.fixture
def setup_api(app, mock_db_manager, mock_emotion_tracker, mock_config):
    """Set up the API with mock dependencies."""
    mock_face_detector = None
    mock_tts_manager = None
    mock_voice_recognition = None
    mock_intent_classifier = None
    mock_context_assistant = None
    mock_model_router = None
    
    # Initialize the API with mock dependencies
    init_api(
        app,
        mock_db_manager,
        mock_emotion_tracker,
        mock_face_detector,
        mock_tts_manager,
        mock_voice_recognition,
        mock_intent_classifier,
        mock_config,
        mock_context_assistant,
        mock_model_router
    )
    
    return {
        "app": app,
        "db_manager": mock_db_manager,
        "emotion_tracker": mock_emotion_tracker,
        "config": mock_config
    }


def test_api_docs(client, setup_api):
    """Test the API documentation endpoint."""
    response = client.get("/api/docs")
    
    assert response.status_code == 200
    assert b"API Documentation" in response.data


def test_get_status(client, setup_api):
    """Test the status endpoint."""
    response = client.get("/api/status")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert "status" in data
    assert data["status"] == "operational"
    assert "version" in data


def test_analyze_emotion(client, setup_api):
    """Test the emotion analysis endpoint."""
    test_text = "I am feeling happy today"
    
    response = client.post(
        "/api/analyze-emotion",
        data=json.dumps({"text": test_text}),
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert "emotion" in data
    assert "primary" in data["emotion"]
    assert data["emotion"]["primary"] == "joy"
    assert "scores" in data["emotion"]
    assert "joy" in data["emotion"]["scores"]
    assert float(data["emotion"]["scores"]["joy"]) > 0.5


def test_analyze_emotion_with_context(client, setup_api):
    """Test emotion analysis with context."""
    test_text = "I feel sad about what happened"
    test_context = ["Yesterday was terrible", "I lost my job"]
    
    response = client.post(
        "/api/analyze-emotion",
        data=json.dumps({
            "text": test_text,
            "context": test_context
        }),
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert "emotion" in data
    assert "primary" in data["emotion"]
    assert data["emotion"]["primary"] == "sadness"


def test_analyze_emotion_no_text(client, setup_api):
    """Test emotion analysis with no text provided."""
    response = client.post(
        "/api/analyze-emotion",
        data=json.dumps({}),
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert "error" in data
    assert "text" in data["error"]