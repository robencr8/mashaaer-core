"""
Voice Tone API for Mashaaer Feelings

Provides REST API endpoints for generating speech with emotional tone modulation.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, Response, send_file
import time

logger = logging.getLogger(__name__)

# Create Blueprint
voice_tone_bp = Blueprint('voice_tone', __name__)

# Global reference to VoiceToneModulator
voice_tone_modulator = None

@voice_tone_bp.route('/api/voice-tone/generate', methods=['POST'])
def generate_emotional_speech():
    """
    Generate speech with emotional tone modulation
    
    Expected JSON request body:
    {
        "text": "Text to convert to speech",
        "emotion": "happy",  # Optional, defaults to "neutral"
        "voice_id": "cosmic_voice_1",  # Optional, uses default if not provided
        "output_format": "mp3",  # Optional, defaults to "mp3"
        "language": "en"  # Optional, defaults to "en"
    }
    
    Returns JSON response:
    {
        "success": true,
        "audio_url": "/api/voice-tone/audio/filename.mp3",
        "emotion": "happy",
        "text": "Original text",
        "duration": 3.5
    }
    
    Or audio file directly if download=true parameter is added to request
    """
    if not voice_tone_modulator:
        logger.error("Voice Tone Modulator not initialized")
        return jsonify({
            "success": False,
            "error": "Voice Tone Modulator not available",
            "message": "Service is temporarily unavailable"
        }), 503
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data or not isinstance(data, dict):
            return jsonify({
                "success": False,
                "error": "Invalid request",
                "message": "Request body must be valid JSON"
            }), 400
            
        # Get parameters from request
        text = data.get("text")
        emotion = data.get("emotion", "neutral")
        voice_id = data.get("voice_id")
        output_format = data.get("output_format", "mp3")
        language = data.get("language", "en")
        
        # Validate required parameters
        if not text:
            return jsonify({
                "success": False,
                "error": "Missing parameter",
                "message": "Text is required"
            }), 400
        
        # Generate speech with emotional tone
        audio_path, metadata = voice_tone_modulator.generate_modulated_speech(
            text=text,
            emotion=emotion,
            voice_id=voice_id,
            output_format=output_format,
            language=language
        )
        
        # Create URL for accessing the audio
        filename = os.path.basename(audio_path)
        audio_url = f"/api/voice-tone/audio/{filename}"
        
        # Return response
        return jsonify({
            "success": True,
            "audio_url": audio_url,
            "emotion": emotion,
            "text": text,
            "duration": metadata.get("duration", 0),
            "filename": filename
        })
    except Exception as e:
        logger.error(f"Error generating emotional speech: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Speech generation failed",
            "message": str(e)
        }), 500

@voice_tone_bp.route('/api/voice-tone/audio/<filename>', methods=['GET'])
def get_audio_file(filename):
    """
    Serve generated audio file
    
    Args:
        filename: Name of the audio file to serve
        
    Returns:
        Audio file response
    """
    try:
        # Security check - only allow alphanumeric, underscore, dash, and extension
        import re
        if not re.match(r'^[\w\-\.]+$', filename):
            logger.warning(f"Suspicious filename requested: {filename}")
            return jsonify({
                "success": False,
                "error": "Invalid filename",
                "message": "Filename contains invalid characters"
            }), 400
        
        # Determine the cache directory based on where TTS files are stored
        base_cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tts_cache')
        if not os.path.exists(base_cache_dir):
            base_cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_sounds')
        
        # Look for the file in potential cache directories
        potential_paths = [
            os.path.join(base_cache_dir, filename),
            os.path.join('tts_cache', filename),
            os.path.join('temp_sounds', filename)
        ]
        
        file_path = None
        for path in potential_paths:
            if os.path.exists(path) and os.path.isfile(path):
                file_path = path
                break
        
        if not file_path:
            logger.warning(f"Audio file not found: {filename}")
            return jsonify({
                "success": False,
                "error": "File not found",
                "message": "The requested audio file does not exist"
            }), 404
        
        # Determine content type based on file extension
        content_type = "audio/mpeg"  # Default to mp3
        if filename.endswith('.wav'):
            content_type = "audio/wav"
        elif filename.endswith('.ogg'):
            content_type = "audio/ogg"
        
        # Serve the file
        return send_file(
            file_path,
            mimetype=content_type,
            as_attachment=request.args.get('download', 'false').lower() == 'true',
            download_name=filename if request.args.get('download', 'false').lower() == 'true' else None
        )
    except Exception as e:
        logger.error(f"Error serving audio file: {str(e)}")
        return jsonify({
            "success": False,
            "error": "File access error",
            "message": str(e)
        }), 500

@voice_tone_bp.route('/api/voice-tone/emotions', methods=['GET'])
def get_available_emotions():
    """
    Get list of available emotions for voice modulation
    
    Returns JSON response:
    {
        "success": true,
        "emotions": [
            {
                "id": "happy",
                "name": "Happy",
                "description": "Speech with happy emotional tone"
            },
            ...
        ]
    }
    """
    if not voice_tone_modulator:
        logger.error("Voice Tone Modulator not initialized")
        return jsonify({
            "success": False,
            "error": "Voice Tone Modulator not available",
            "message": "Service is temporarily unavailable"
        }), 503
    
    try:
        emotions = voice_tone_modulator.get_available_emotions()
        return jsonify({
            "success": True,
            "emotions": emotions
        })
    except Exception as e:
        logger.error(f"Error getting available emotions: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to get emotions",
            "message": str(e)
        }), 500

@voice_tone_bp.route('/api/voice-tone/status', methods=['GET'])
def get_voice_tone_status():
    """
    Get status of Voice Tone Modulator
    
    Returns JSON response:
    {
        "success": true,
        "available": true,
        "has_emotion_modulator": true,
        "has_tts_manager": true
    }
    """
    available = False
    has_emotion_modulator = False
    has_tts_manager = False
    
    if voice_tone_modulator:
        available = voice_tone_modulator.is_available()
        has_tts_manager = voice_tone_modulator.tts_manager is not None
        has_emotion_modulator = (
            voice_tone_modulator.emotion_modulator is not None and
            voice_tone_modulator.emotion_modulator.is_available()
        )
    
    return jsonify({
        "success": True,
        "available": available,
        "has_emotion_modulator": has_emotion_modulator,
        "has_tts_manager": has_tts_manager,
        "timestamp": time.time()
    })

def init_voice_tone_api(app, modulator):
    """
    Initialize Voice Tone API
    
    Args:
        app: Flask application instance
        modulator: Instance of VoiceToneModulator
        
    Returns:
        Blueprint for Voice Tone API
    """
    global voice_tone_modulator
    voice_tone_modulator = modulator
    
    # Register blueprint with the Flask app
    app.register_blueprint(voice_tone_bp)
    
    logger.info("Voice Tone API initialized")
    return voice_tone_bp