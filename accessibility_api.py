"""
Accessibility API Routes for Mashaaer Feelings Application

Provides API endpoints for the Accessibility Voice Guidance Narrator,
allowing control of accessibility features through RESTful API calls.
"""

import os
import logging
import json
from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any, Optional

from accessibility_narrator import AccessibilityNarrator, create_accessibility_narrator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint for accessibility API routes
accessibility_api = Blueprint('accessibility_api', __name__)

# Global narrator instance
narrator = None

def init_accessibility_api(app, tts_manager=None, voice_tone_modulator=None):
    """
    Initialize the Accessibility API with required dependencies
    
    Args:
        app: Flask application instance
        tts_manager: Text-to-Speech manager instance
        voice_tone_modulator: Voice Tone Modulator instance
    """
    global narrator
    
    # Initialize the accessibility narrator
    config_path = os.path.join('config', 'accessibility_config.json')
    narrator = create_accessibility_narrator(
        tts_manager=tts_manager,
        voice_tone_modulator=voice_tone_modulator,
        config_path=config_path
    )
    
    # Register the blueprint with the app
    app.register_blueprint(accessibility_api, url_prefix='/api/accessibility')
    
    logger.info("Accessibility API routes registered successfully")
    return narrator

def get_narrator() -> Optional[AccessibilityNarrator]:
    """
    Get the global narrator instance
    
    Returns:
        AccessibilityNarrator instance or None if not initialized
    """
    return narrator

@accessibility_api.route('/status', methods=['GET'])
def get_status():
    """
    Get the status of the accessibility narrator
    
    Returns:
        JSON object with narrator status
    """
    if not narrator:
        return jsonify({
            "success": False,
            "error": "Accessibility narrator not initialized"
        }), 500
    
    return jsonify({
        "success": True,
        "enabled": narrator.is_enabled(),
        "config": narrator.get_settings()
    })

@accessibility_api.route('/toggle', methods=['POST'])
def toggle_narrator():
    """
    Toggle the accessibility narrator on or off
    
    Expected request body (optional):
    {
        "enabled": true    # To explicitly set state, omit to toggle
    }
    
    Returns:
        JSON with new narrator state
    """
    if not narrator:
        return jsonify({
            "success": False,
            "error": "Accessibility narrator not initialized"
        }), 500
    
    # Get request data
    data = request.get_json(silent=True) or {}
    
    # Toggle or set enabled state
    if 'enabled' in data:
        enabled = bool(data['enabled'])
        new_state = narrator.toggle_narrator(enabled)
    else:
        new_state = narrator.toggle_narrator()
    
    return jsonify({
        "success": True,
        "enabled": new_state
    })

@accessibility_api.route('/settings', methods=['GET'])
def get_settings():
    """
    Get current accessibility settings
    
    Returns:
        JSON object with current settings
    """
    if not narrator:
        return jsonify({
            "success": False,
            "error": "Accessibility narrator not initialized"
        }), 500
    
    return jsonify({
        "success": True,
        "settings": narrator.get_settings()
    })

@accessibility_api.route('/settings', methods=['POST'])
def update_settings():
    """
    Update accessibility settings
    
    Expected request body:
    {
        "settings": {
            "default_language": "ar",
            "speaking_rate": 1.2,
            "verbosity_level": "high",
            ...
        }
    }
    
    Returns:
        JSON with updated settings
    """
    if not narrator:
        return jsonify({
            "success": False,
            "error": "Accessibility narrator not initialized"
        }), 500
    
    # Get request data
    data = request.get_json(silent=True) or {}
    settings = data.get('settings', {})
    
    if not settings:
        return jsonify({
            "success": False,
            "error": "No settings provided"
        }), 400
    
    # Update settings
    narrator.update_settings(settings)
    
    # Save settings to configuration file
    config_path = os.path.join('config', 'accessibility_config.json')
    narrator.save_config(config_path)
    
    return jsonify({
        "success": True,
        "settings": narrator.get_settings()
    })

@accessibility_api.route('/language', methods=['POST'])
def set_language():
    """
    Set the narrator language
    
    Expected request body:
    {
        "language": "en"    # or "ar"
    }
    
    Returns:
        JSON with success status
    """
    if not narrator:
        return jsonify({
            "success": False,
            "error": "Accessibility narrator not initialized"
        }), 500
    
    # Get request data
    data = request.get_json(silent=True) or {}
    language = data.get('language')
    
    if not language or language not in ['en', 'ar']:
        return jsonify({
            "success": False,
            "error": "Invalid or missing language code"
        }), 400
    
    # Set language
    narrator.set_language(language)
    
    return jsonify({
        "success": True,
        "language": language
    })

@accessibility_api.route('/verbosity', methods=['POST'])
def set_verbosity():
    """
    Set the verbosity level for the narrator
    
    Expected request body:
    {
        "level": "medium"    # "low", "medium", or "high"
    }
    
    Returns:
        JSON with success status
    """
    if not narrator:
        return jsonify({
            "success": False,
            "error": "Accessibility narrator not initialized"
        }), 500
    
    # Get request data
    data = request.get_json(silent=True) or {}
    level = data.get('level')
    
    if not level or level not in ['low', 'medium', 'high']:
        return jsonify({
            "success": False,
            "error": "Invalid or missing verbosity level"
        }), 400
    
    # Set verbosity
    narrator.set_verbosity(level)
    
    return jsonify({
        "success": True,
        "verbosity": level
    })

@accessibility_api.route('/speaking-rate', methods=['POST'])
def set_speaking_rate():
    """
    Set the speaking rate for the narrator
    
    Expected request body:
    {
        "rate": 1.0    # 0.5 to 2.0
    }
    
    Returns:
        JSON with success status
    """
    if not narrator:
        return jsonify({
            "success": False,
            "error": "Accessibility narrator not initialized"
        }), 500
    
    # Get request data
    data = request.get_json(silent=True) or {}
    
    try:
        rate = float(data.get('rate', 1.0))
        # Constrain rate to reasonable bounds
        rate = max(0.5, min(2.0, rate))
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "error": "Invalid speaking rate"
        }), 400
    
    # Set speaking rate
    narrator.set_speaking_rate(rate)
    
    return jsonify({
        "success": True,
        "rate": rate
    })

@accessibility_api.route('/speak', methods=['POST'])
def speak_text():
    """
    Make the narrator speak text
    
    Expected request body:
    {
        "text": "Text to speak",
        "language": "en",      # Optional, defaults to current language
        "priority": false,     # Optional, whether to interrupt current speech
        "emotion": "happy"     # Optional, for emotional speech
    }
    
    Returns:
        JSON with success status
    """
    if not narrator:
        return jsonify({
            "success": False,
            "error": "Accessibility narrator not initialized"
        }), 500
    
    # Get request data
    data = request.get_json(silent=True) or {}
    text = data.get('text')
    
    if not text:
        return jsonify({
            "success": False,
            "error": "Missing text to speak"
        }), 400
    
    # Optional parameters
    language = data.get('language')
    priority = data.get('priority', False)
    emotion = data.get('emotion')
    
    # Override language if specified
    if language:
        current_language = narrator.config.get('default_language')
        narrator.set_language(language)
    
    # Speak with or without emotion
    if emotion and narrator.voice_tone_modulator:
        narrator.speak_with_emotion(text, emotion, priority)
    else:
        narrator.speak(text, priority)
    
    # Restore original language if it was temporarily changed
    if language:
        narrator.set_language(current_language)
    
    return jsonify({
        "success": True,
        "message": "Speech queued"
    })

@accessibility_api.route('/guide', methods=['POST'])
def guide_user():
    """
    Provide guidance based on screen and context
    
    Expected request body:
    {
        "screen": "main",       # Screen identifier
        "context": "initial"    # Optional context within the screen
    }
    
    Returns:
        JSON with success status
    """
    if not narrator:
        return jsonify({
            "success": False,
            "error": "Accessibility narrator not initialized"
        }), 500
    
    # Get request data
    data = request.get_json(silent=True) or {}
    screen = data.get('screen')
    
    if not screen:
        return jsonify({
            "success": False,
            "error": "Missing screen identifier"
        }), 400
    
    # Optional context
    context = data.get('context', 'initial')
    
    # Provide guidance
    narrator.guide_user(screen, context)
    
    return jsonify({
        "success": True,
        "message": f"Guidance provided for {screen}/{context}"
    })

@accessibility_api.route('/announce-navigation', methods=['POST'])
def announce_navigation():
    """
    Announce navigation to a new screen
    
    Expected request body:
    {
        "screen": "settings"    # Destination screen
    }
    
    Returns:
        JSON with success status
    """
    if not narrator:
        return jsonify({
            "success": False,
            "error": "Accessibility narrator not initialized"
        }), 500
    
    # Get request data
    data = request.get_json(silent=True) or {}
    screen = data.get('screen')
    
    if not screen:
        return jsonify({
            "success": False,
            "error": "Missing destination screen"
        }), 400
    
    # Announce navigation
    narrator.announce_navigation(screen)
    
    return jsonify({
        "success": True,
        "message": f"Navigation to {screen} announced"
    })

@accessibility_api.route('/announce-element', methods=['POST'])
def announce_element():
    """
    Announce an element the user is interacting with
    
    Expected request body:
    {
        "element_type": "button",
        "content": "Submit",               # Optional
        "additional_info": "Sends form"    # Optional
    }
    
    Returns:
        JSON with success status
    """
    if not narrator:
        return jsonify({
            "success": False,
            "error": "Accessibility narrator not initialized"
        }), 500
    
    # Get request data
    data = request.get_json(silent=True) or {}
    element_type = data.get('element_type')
    
    if not element_type:
        return jsonify({
            "success": False,
            "error": "Missing element type"
        }), 400
    
    # Optional parameters
    content = data.get('content', '')
    additional_info = data.get('additional_info', '')
    
    # Announce element
    narrator.announce_element(element_type, content, additional_info)
    
    return jsonify({
        "success": True,
        "message": f"Element {element_type} announced"
    })

@accessibility_api.route('/announce-emotion', methods=['POST'])
def announce_emotion():
    """
    Announce detected emotion
    
    Expected request body:
    {
        "emotion": "happy",
        "intensity": "high"    # Optional
    }
    
    Returns:
        JSON with success status
    """
    if not narrator:
        return jsonify({
            "success": False,
            "error": "Accessibility narrator not initialized"
        }), 500
    
    # Get request data
    data = request.get_json(silent=True) or {}
    emotion = data.get('emotion')
    
    if not emotion:
        return jsonify({
            "success": False,
            "error": "Missing emotion"
        }), 400
    
    # Optional intensity
    intensity = data.get('intensity')
    
    # Announce emotion
    narrator.announce_emotion(emotion, intensity)
    
    return jsonify({
        "success": True,
        "message": f"Emotion {emotion} announced"
    })

@accessibility_api.route('/help', methods=['POST'])
def provide_help():
    """
    Provide contextual help based on current screen
    
    Returns:
        JSON with success status
    """
    if not narrator:
        return jsonify({
            "success": False,
            "error": "Accessibility narrator not initialized"
        }), 500
    
    # Provide help
    narrator.provide_help()
    
    return jsonify({
        "success": True,
        "message": "Help provided"
    })

def register_accessibility_routes(app, tts_manager=None, voice_tone_modulator=None):
    """
    Register accessibility routes with the Flask application
    
    Args:
        app: Flask application instance
        tts_manager: Text-to-Speech manager instance
        voice_tone_modulator: Voice Tone Modulator instance
        
    Returns:
        Initialized narrator instance
    """
    return init_accessibility_api(app, tts_manager, voice_tone_modulator)