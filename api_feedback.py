"""
API Feedback Routes for Mashaaer Feelings
Provides endpoints for emotion-driven feedback with visual/audio effects
"""

import os
import json
import logging
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app, render_template_string
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create blueprint for API feedback routes
api_feedback_bp = Blueprint('api_feedback', __name__)

@api_feedback_bp.route('/api/direct-feedback', methods=['POST'])
def process_direct_feedback():
    """
    Process direct feedback with emotion-driven response
    
    Expected JSON request body:
    {
        "name": "User Name",          // Optional, defaults to "Anonymous"
        "feedback": "Feedback text",  // Required
        "rating": 4,                  // Optional rating (1-5)
        "emotion": "happy",           // Optional detected emotion
        "timestamp": "ISO timestamp"  // Optional, server will add if missing
    }
    
    Returns JSON response:
    {
        "success": true,
        "message": "Thank you for your feedback!",
        "timestamp": "ISO timestamp",
        "emotion_effect": "happy",     // For triggering UI effects
        "sound_effect": "/static/sounds/success.mp3"
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided",
                "error": "Missing request body"
            }), 400
            
        # Validate required fields
        if "feedback" not in data or not data["feedback"].strip():
            return jsonify({
                "success": False,
                "message": "Feedback text is required",
                "error": "Missing required field: feedback"
            }), 400
            
        # Prepare feedback data with defaults for optional fields
        feedback_data = {
            "name": data.get("name", "Anonymous").strip(),
            "feedback": data["feedback"].strip(),
            "rating": max(1, min(5, int(data.get("rating", 3)))),  # Ensure rating is 1-5
            "emotion": data.get("emotion", "neutral"),
            "timestamp": data.get("timestamp", datetime.now().isoformat()),
            "user_agent": request.headers.get("User-Agent", "Unknown"),
            "ip_address": request.remote_addr
        }
        
        # Log the feedback
        logger.info(f"Received feedback: {json.dumps(feedback_data)}")
        
        # Save feedback to database or file
        save_feedback(feedback_data)
        
        # Determine appropriate emotion effect based on rating/emotion
        emotion_effect = determine_emotion_effect(feedback_data)
        
        # Create response with appropriate effects
        response = {
            "success": True,
            "message": "Thank you for your feedback!",
            "timestamp": datetime.now().isoformat(),
            "emotion_effect": emotion_effect,
            "sound_effect": f"/static/sounds/{get_sound_for_emotion(emotion_effect)}"
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while processing your feedback",
            "error": str(e),
            "emotion_effect": "confused",
            "sound_effect": "/static/sounds/error.mp3"
        }), 500

@api_feedback_bp.route('/api/feedback/emotions', methods=['GET'])
def get_available_emotions():
    """
    Get a list of available emotions for feedback
    
    Returns:
    {
        "emotions": [
            {
                "id": "happy",
                "name": "Happy",
                "icon": "😊",
                "color": "#FFD700"
            },
            ...
        ]
    }
    """
    emotions = [
        {
            "id": "happy",
            "name": "Happy",
            "icon": "😊",
            "color": "#FFD700"
        },
        {
            "id": "sad",
            "name": "Sad",
            "icon": "😢",
            "color": "#4169E1"
        },
        {
            "id": "angry",
            "name": "Angry",
            "icon": "😠",
            "color": "#FF4500"
        },
        {
            "id": "calm",
            "name": "Calm",
            "icon": "😌",
            "color": "#48D1CC"
        },
        {
            "id": "excited",
            "name": "Excited",
            "icon": "🤩",
            "color": "#FF1493"
        },
        {
            "id": "confused",
            "name": "Confused",
            "icon": "😕",
            "color": "#9932CC"
        },
        {
            "id": "neutral",
            "name": "Neutral",
            "icon": "😐",
            "color": "#9370DB"
        }
    ]
    
    return jsonify({"emotions": emotions})

@api_feedback_bp.route('/api/feedback/sounds/<emotion>', methods=['GET'])
def get_emotion_sound(emotion):
    """
    Get the URL for an emotion-specific sound effect
    
    Args:
        emotion: The emotion to get sound for
        
    Returns:
    {
        "sound_url": "/static/sounds/happy.mp3"
    }
    """
    sound_url = f"/static/sounds/{get_sound_for_emotion(emotion)}"
    return jsonify({"sound_url": sound_url})

def determine_emotion_effect(feedback_data: Dict[str, Any]) -> str:
    """
    Determine the appropriate emotion effect based on feedback data
    
    Args:
        feedback_data: The feedback data including rating and emotion
        
    Returns:
        String ID of the determined emotion effect
    """
    # If explicit emotion is provided, use it
    if "emotion" in feedback_data and feedback_data["emotion"]:
        return feedback_data["emotion"]
        
    # Otherwise determine from rating
    rating = feedback_data.get("rating", 3)
    
    if rating >= 4:
        return "happy"
    elif rating == 3:
        return "neutral"
    else:
        return "sad"

def get_sound_for_emotion(emotion: str) -> str:
    """
    Get the appropriate sound file for an emotion
    
    Args:
        emotion: The emotion to get sound for
        
    Returns:
        String filename for the sound
    """
    emotion_sounds = {
        "happy": "success.mp3",
        "sad": "transition.mp3",
        "angry": "error.mp3",
        "calm": "hover.mp3",
        "excited": "success.mp3",
        "confused": "error.mp3",
        "neutral": "click.mp3"
    }
    
    return emotion_sounds.get(emotion, "click.mp3")

def save_feedback(feedback_data: Dict[str, Any]) -> bool:
    """
    Save feedback data to database or file
    
    Args:
        feedback_data: The feedback data to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create feedback directory if it doesn't exist
        feedback_dir = os.path.join(current_app.root_path, 'data', 'feedback')
        os.makedirs(feedback_dir, exist_ok=True)
        
        # Generate unique filename based on timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"feedback_{timestamp}.json"
        file_path = os.path.join(feedback_dir, filename)
        
        # Save feedback to JSON file
        with open(file_path, 'w') as f:
            json.dump(feedback_data, f, indent=2)
            
        logger.info(f"Feedback saved to {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving feedback: {str(e)}")
        return False

def register_api_feedback_routes(app):
    """Register API feedback routes with the Flask application"""
    app.register_blueprint(api_feedback_bp)
    logger.info("API feedback routes registered successfully")
    
    # Create feedback data directory if needed
    feedback_dir = os.path.join(app.root_path, 'data', 'feedback')
    os.makedirs(feedback_dir, exist_ok=True)