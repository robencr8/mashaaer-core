"""
Voice Logic API for Mashaaer Feelings
Provides endpoints for text-to-speech with language detection
"""

import os
import hashlib
import logging
from flask import Blueprint, request, jsonify, send_from_directory
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from gtts import gTTS
import time

# Configure logger
logger = logging.getLogger(__name__)

# Create Blueprint
voice_bp = Blueprint('voice_logic', __name__, url_prefix='/api')

# Configure voice parameters
VOICE_CACHE_DIR = os.path.join(os.getcwd(), 'tts_cache')
os.makedirs(VOICE_CACHE_DIR, exist_ok=True)

def init_voice_logic(app):
    """Initialize the voice logic blueprint with necessary dependencies"""
    logger.info("Initializing voice logic API")
    app.register_blueprint(voice_bp)
    return voice_bp

@voice_bp.route('/voice_logic', methods=['POST'])
def voice_logic():
    """
    Process text and convert to speech with appropriate language voice
    
    Request body:
    {
        "text": "The text to be converted to speech",
        "language": "auto|en|ar",  (optional - auto-detect if not provided or set to "auto")
        "voice": "default",  (optional - uses language-appropriate voice)
        "use_cache": true  (optional - defaults to true)
    }
    
    Returns:
    {
        "success": true,
        "audio_url": "/tts_cache/audio123.mp3",
        "detected_language": "en",
        "cache_hit": false
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required parameter: text"
            }), 400
        
        text = data.get('text')
        language = data.get('language', 'auto')
        voice = data.get('voice', 'default')
        use_cache = data.get('use_cache', True)
        
        # Auto-detect language if needed
        detected_language = language
        if language == 'auto':
            try:
                detected_language = detect(text)
                # Map to supported languages
                if detected_language.startswith('ar'):
                    detected_language = 'ar'
                else:
                    detected_language = 'en'  # Fallback to English for other languages
            except LangDetectException:
                logger.warning(f"Language detection failed for: {text}")
                detected_language = 'en'  # Default to English on failure
        
        # Generate cache key based on text and language
        cache_key = hashlib.md5(f"{text}_{detected_language}_{voice}".encode()).hexdigest()
        cache_filename = f"{cache_key}.mp3"
        cache_path = os.path.join(VOICE_CACHE_DIR, cache_filename)
        cache_url = f"/tts_cache/{cache_filename}"
        
        cache_hit = False
        
        # Check cache if enabled
        if use_cache and os.path.exists(cache_path):
            logger.debug(f"Voice cache hit for: {text[:30]}...")
            cache_hit = True
        else:
            # Generate TTS file
            logger.debug(f"Generating TTS for: {text[:30]}... in language: {detected_language}")
            
            try:
                tts = gTTS(text=text, lang=detected_language)
                tts.save(cache_path)
                
                # Short delay to ensure file is written
                time.sleep(0.1)
                
                logger.debug(f"TTS generated successfully: {cache_path}")
            except Exception as e:
                logger.error(f"TTS generation error: {str(e)}")
                return jsonify({
                    "success": False,
                    "error": f"Failed to generate speech: {str(e)}"
                }), 500
        
        return jsonify({
            "success": True,
            "audio_url": cache_url,
            "detected_language": detected_language,
            "cache_hit": cache_hit
        })
    
    except Exception as e:
        logger.error(f"Voice logic error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@voice_bp.route('/tts_cache/<filename>', methods=['GET'])
def serve_voice_file(filename):
    """
    Serve voice audio files from the TTS cache
    
    Args:
        filename: The filename of the audio file to serve
        
    Returns:
        The audio file as a response with appropriate MIME type
    """
    try:
        logger.debug(f"Serving TTS file: {filename}")
        return send_from_directory(VOICE_CACHE_DIR, filename, mimetype='audio/mpeg')
    except Exception as e:
        logger.error(f"Error serving TTS file {filename}: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"File not found: {str(e)}"
        }), 404