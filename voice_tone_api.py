"""
Voice Tone Modulation API for Mashaaer Feelings
Provides endpoints for voice tone modulation based on detected emotions
"""

import os
import json
import logging
from flask import Blueprint, request, jsonify, current_app
from voice_tone_modulator import VoiceToneModulator

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
voice_tone_bp = Blueprint('voice_tone', __name__, url_prefix='/api')

# Global voice tone modulator instance
voice_tone_modulator = None

def init_voice_tone_api(app, emotion_modulator=None, tts_manager=None):
    """
    Initialize the voice tone modulation API
    
    Args:
        app: Flask application instance
        emotion_modulator: EmotionModulator instance
        tts_manager: TTS manager instance
    """
    global voice_tone_modulator
    
    logger.info("Initializing voice tone modulation API")
    
    # Register blueprint
    app.register_blueprint(voice_tone_bp)
    
    # Initialize the voice tone modulator
    voice_tone_modulator = VoiceToneModulator(
        emotion_modulator=emotion_modulator,
        tts_manager=tts_manager
    )
    
    logger.info("Voice tone modulation API initialized")
    return voice_tone_bp

@voice_tone_bp.route('/voice_tone', methods=['POST'])
def voice_tone():
    """
    Modulate voice tone based on detected emotion
    
    Request body:
    {
        "text": "The text to speak",
        "detected_emotion": "happy/sad/angry/etc.",
        "target_emotion": "happy/neutral/etc." (optional, will determine appropriate response emotion if not provided),
        "language": "en/ar" (optional, defaults to "en"),
        "voice": "default/specific-voice-id" (optional, defaults to language-appropriate voice)
    }
    
    Returns:
    {
        "success": true,
        "audio_url": "/tts_cache/modulated_audio123.mp3",
        "modulated_text": "The modulated text...",
        "emotion": "happy",
        "original_text": "The original text...",
        "voice_params": {
            "pitch": 1.2,
            "speed": 1.15,
            ...
        }
    }
    """
    global voice_tone_modulator
    
    try:
        # Parse request data
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required parameter: text"
            }), 400
        
        text = data.get('text')
        detected_emotion = data.get('detected_emotion', 'neutral')
        target_emotion = data.get('target_emotion')  # Optional
        language = data.get('language', 'en')
        voice = data.get('voice', 'default')
        
        # Check if voice tone modulator is initialized
        if not voice_tone_modulator:
            return jsonify({
                "success": False,
                "error": "Voice tone modulator not initialized"
            }), 500
        
        # Apply voice modulation
        result = voice_tone_modulator.apply_voice_modulation(
            text=text,
            detected_emotion=detected_emotion,
            target_emotion=target_emotion,
            language=language,
            voice=voice
        )
        
        if not result.get('success', False):
            return jsonify({
                "success": False,
                "error": result.get('error', 'Unknown error during voice modulation')
            }), 500
        
        # Create response with audio URL
        audio_path = result.get('audio_path')
        
        # Convert file path to URL
        base_url = current_app.config.get('APP_URL', '')
        audio_url = f"{base_url}/{audio_path}" if audio_path else None
        
        return jsonify({
            "success": True,
            "audio_url": audio_url,
            "modulated_text": result.get('modulated_text'),
            "emotion": result.get('emotion'),
            "original_text": text,
            "voice_params": result.get('params_applied', {})
        })
        
    except Exception as e:
        logger.error(f"Voice tone modulation error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@voice_tone_bp.route('/voice_tone/emotions', methods=['GET'])
def get_emotions():
    """
    Get available emotions for voice tone modulation
    
    Returns:
    {
        "success": true,
        "emotions": [
            {
                "id": "happy",
                "name": "Happy",
                "description": "Cheerful, upbeat tone"
            },
            ...
        ]
    }
    """
    global voice_tone_modulator
    
    try:
        # Check if voice tone modulator is initialized
        if not voice_tone_modulator:
            return jsonify({
                "success": False,
                "error": "Voice tone modulator not initialized"
            }), 500
        
        # Get emotions from voice_emotion_params
        emotions = []
        
        emotion_descriptions = {
            "happy": "Cheerful, upbeat tone with higher pitch and faster speech",
            "sad": "Somber, empathetic tone with lower pitch and slower speech",
            "angry": "Controlled, steady tone with measured pace and clarity",
            "fearful": "Reassuring, supportive tone with balanced parameters",
            "surprised": "Engaged, curious tone with slightly elevated pitch",
            "neutral": "Balanced, natural tone with standard parameters"
        }
        
        for emotion_id, params in voice_tone_modulator.voice_emotion_params.items():
            emotions.append({
                "id": emotion_id,
                "name": emotion_id.capitalize(),
                "description": emotion_descriptions.get(emotion_id, "Custom tone configuration"),
                "voice_quality": params.get("voice_quality", "balanced")
            })
        
        return jsonify({
            "success": True,
            "emotions": emotions
        })
        
    except Exception as e:
        logger.error(f"Error fetching emotions: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@voice_tone_bp.route('/voice_tone/test', methods=['GET'])
def test_voice_tone():
    """
    Test endpoint for voice tone modulation
    
    Query parameters:
        emotion: Emotion to test (happy, sad, angry, etc.)
        language: Language code (en, ar)
    
    Returns:
        Audio file with test message in the requested emotional tone
    """
    global voice_tone_modulator
    
    try:
        # Get query parameters
        emotion = request.args.get('emotion', 'neutral')
        language = request.args.get('language', 'en')
        
        # Check if voice tone modulator is initialized
        if not voice_tone_modulator:
            return jsonify({
                "success": False,
                "error": "Voice tone modulator not initialized"
            }), 500
        
        # Create test messages for each language
        test_messages = {
            "en": {
                "happy": "I'm really excited to share this news with you! It's going to be amazing!",
                "sad": "I understand this is a difficult time. I'm here to support you through it.",
                "angry": "I appreciate your patience while we resolve this issue. Let's find a solution together.",
                "fearful": "Don't worry, we'll get through this step by step. You're not alone.",
                "surprised": "Oh, that's unexpected! Let's explore what this means together.",
                "neutral": "Here is the information you requested. Let me know if you need anything else."
            },
            "ar": {
                "happy": "أنا متحمس جدًا لمشاركة هذا الخبر معك! سيكون رائعًا!",
                "sad": "أتفهم أن هذا وقت صعب. أنا هنا لدعمك خلاله.",
                "angry": "أقدر صبرك بينما نحل هذه المشكلة. دعنا نجد حلاً معًا.",
                "fearful": "لا تقلق، سنتجاوز هذا خطوة بخطوة. أنت لست وحدك.",
                "surprised": "أوه، هذا غير متوقع! دعنا نستكشف ماذا يعني ذلك معًا.",
                "neutral": "هنا المعلومات التي طلبتها. أخبرني إذا كنت بحاجة إلى أي شيء آخر."
            }
        }
        
        # Get the test message
        test_message = test_messages.get(language, test_messages["en"]).get(emotion, test_messages[language]["neutral"])
        
        # Apply voice modulation
        result = voice_tone_modulator.apply_voice_modulation(
            text=test_message,
            detected_emotion="neutral",  # We're testing a specific target emotion
            target_emotion=emotion,
            language=language
        )
        
        if not result.get('success', False):
            return jsonify({
                "success": False,
                "error": result.get('error', 'Unknown error during voice modulation')
            }), 500
        
        # Create response with audio URL
        audio_path = result.get('audio_path')
        
        # Convert file path to URL
        base_url = current_app.config.get('APP_URL', '')
        audio_url = f"{base_url}/{audio_path}" if audio_path else None
        
        return jsonify({
            "success": True,
            "audio_url": audio_url,
            "modulated_text": result.get('modulated_text'),
            "emotion": emotion,
            "original_text": test_message
        })
        
    except Exception as e:
        logger.error(f"Voice tone test error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500