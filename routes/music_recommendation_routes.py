"""
Music Recommendation Routes for Mashaaer Feelings Application

This module provides API routes for getting mood-based music recommendations
to enhance the emotional learning experience.
"""

import logging
from typing import Dict, Any

from flask import Blueprint, request, jsonify, current_app

from services.music_recommendation_service import MusicRecommendationService


# Configure logger
logger = logging.getLogger(__name__)

# Create Blueprint
music_recommendation_bp = Blueprint('music_recommendation', __name__, url_prefix='/api/music')


@music_recommendation_bp.route('/recommendations', methods=['POST'])
def get_recommendations():
    """
    Get music recommendations based on emotion
    
    Expected request body:
    {
        "emotion": "happiness",
        "intensity": 0.8,          // optional
        "user_preferences": {      // optional
            "preferred_genres": ["pop", "electronic", "indie"],
            "preferred_tempo": "fast"
        },
        "limit": 2                 // optional
    }
    
    Returns:
        JSON with recommendations
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        if 'emotion' not in data:
            return jsonify({'success': False, 'error': 'Missing required field: emotion'}), 400
        
        # Get recommendations
        result = MusicRecommendationService.get_recommendations(
            emotion=data['emotion'],
            intensity=data.get('intensity'),
            user_preferences=data.get('user_preferences'),
            limit=data.get('limit', 2)
        )
        
        if 'error' in result and not result.get('success', False):
            return jsonify({'success': False, 'error': result['error']}), 400
            
        return jsonify({'success': True, 'data': result}), 200
        
    except Exception as e:
        logger.error(f"Error in get_recommendations route: {str(e)}")
        return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500


@music_recommendation_bp.route('/emotions', methods=['GET'])
def get_available_emotions():
    """
    Get list of available emotions for recommendations
    
    Returns:
        JSON with available emotions
    """
    try:
        emotions = MusicRecommendationService.get_available_emotions()
        
        return jsonify({
            'success': True,
            'data': emotions
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_available_emotions route: {str(e)}")
        return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500


@music_recommendation_bp.route('/characteristics', methods=['GET'])
def get_emotion_music_characteristics():
    """
    Get music characteristics for each emotion
    
    Returns:
        JSON with emotion to music characteristics mapping
    """
    try:
        return jsonify({
            'success': True,
            'data': MusicRecommendationService.EMOTION_MUSIC_MAPPING
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_emotion_music_characteristics route: {str(e)}")
        return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500


def register_routes(app):
    """Register routes with the Flask application"""
    app.register_blueprint(music_recommendation_bp)
    logger.info("Music recommendation routes registered")