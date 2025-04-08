"""
API Emotion Test Routes
Provides test endpoints for the emotion modulation features
"""

import os
import json
import logging
from flask import Blueprint, request, jsonify

from emotion_modulator import EmotionModulator

logger = logging.getLogger(__name__)

# Create Blueprint
emotion_test_bp = Blueprint('emotion_test', __name__)

# Initialize emotion modulator
try:
    emotion_modulator = EmotionModulator()
    if emotion_modulator.is_available():
        logger.info("Emotion modulator initialized successfully for testing")
    else:
        logger.warning("Emotion modulator is not available for testing")
except Exception as e:
    emotion_modulator = None
    logger.error(f"Failed to initialize emotion modulator for testing: {str(e)}")

@emotion_test_bp.route('/api/test/emotion/analyze', methods=['POST'])
def test_analyze_emotion():
    """
    Test emotion analysis functionality
    
    Expected request:
    {
        "text": "The text to analyze"
    }
    """
    try:
        # Get request data
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Get text
        text = data.get('text')
        if not text:
            return jsonify({"error": "No text provided"}), 400
            
        # Check if emotion modulator is available
        if not emotion_modulator or not emotion_modulator.is_available():
            return jsonify({
                "error": "Emotion modulator not available",
                "result": {"emotion": "neutral", "confidence": 0.5}
            }), 200
            
        # Analyze emotion
        result = emotion_modulator.analyze_emotion(text)
        
        # Return result
        return jsonify({
            "success": True,
            "result": result
        })
    
    except Exception as e:
        logger.error(f"Error in emotion analysis test: {str(e)}")
        return jsonify({
            "error": f"Error analyzing emotion: {str(e)}"
        }), 500

@emotion_test_bp.route('/api/test/emotion/modulate', methods=['POST'])
def test_modulate_text():
    """
    Test emotion modulation functionality
    
    Expected request:
    {
        "text": "The text to modulate",
        "target_emotion": "happy", # Optional, defaults to "neutral"
        "user_emotion": "sad",     # Optional
        "language": "en"           # Optional, defaults to "en"
    }
    """
    try:
        # Get request data
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Get text
        text = data.get('text')
        if not text:
            return jsonify({"error": "No text provided"}), 400
            
        # Get options
        target_emotion = data.get('target_emotion', 'neutral')
        user_emotion = data.get('user_emotion')
        language = data.get('language', 'en')
        
        # Check if emotion modulator is available
        if not emotion_modulator or not emotion_modulator.is_available():
            return jsonify({
                "error": "Emotion modulator not available",
                "original_text": text,
                "modulated_text": text
            }), 200
            
        # Modulate text
        modulated_text = emotion_modulator.modulate_text(
            text, 
            target_emotion=target_emotion,
            user_emotion=user_emotion,
            language=language
        )
        
        # Return result
        return jsonify({
            "success": True,
            "original_text": text,
            "modulated_text": modulated_text,
            "target_emotion": target_emotion,
            "user_emotion": user_emotion,
            "language": language
        })
    
    except Exception as e:
        logger.error(f"Error in emotion modulation test: {str(e)}")
        return jsonify({
            "error": f"Error modulating text: {str(e)}"
        }), 500

def register_emotion_test_routes(app):
    """Register emotion test routes with the Flask application"""
    app.register_blueprint(emotion_test_bp)
    logger.info("Registered emotion test routes")