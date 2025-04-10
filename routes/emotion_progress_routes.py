"""
Emotion Progress Routes for Mashaaer Feelings Application

This module provides API routes for tracking and updating emotional learning progress,
managing achievements, and updating learning paths.
"""

import logging
from typing import Dict, Any

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.exc import SQLAlchemyError

from services.emotion_progress_service import EmotionProgressService
from models.emotion_progress import EmotionType, ProgressLevel


# Configure logger
logger = logging.getLogger(__name__)

# Create Blueprint
emotion_progress_bp = Blueprint('emotion_progress', __name__, url_prefix='/api/progress')


@emotion_progress_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_progress(user_id: int):
    """
    Get a complete picture of a user's emotional learning progress
    
    Args:
        user_id: ID of the user
        
    Returns:
        JSON with complete progress information
    """
    try:
        result = EmotionProgressService.get_user_progress(user_id)
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 400
            
        return jsonify({'success': True, 'data': result}), 200
        
    except Exception as e:
        logger.error(f"Error in get_user_progress route: {str(e)}")
        return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500


@emotion_progress_bp.route('/emotion/record', methods=['POST'])
def record_emotion_interaction():
    """
    Record an emotion interaction and update progress
    
    Expected request body:
    {
        "user_id": 1,
        "emotion_type": "happiness",
        "correct": true,
        "context": "While reviewing photos",
        "trigger": "Family memories",
        "intensity": 0.8,
        "notes": "Strong positive reaction"
    }
    
    Returns:
        JSON with update results and earned achievements
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        required_fields = ['user_id', 'emotion_type', 'correct']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Validate emotion type
        if data['emotion_type'] not in [e.value for e in EmotionType]:
            return jsonify({
                'success': False, 
                'error': f'Invalid emotion type. Must be one of: {", ".join([e.value for e in EmotionType])}'
            }), 400
        
        # Process the record
        result = EmotionProgressService.record_emotion_interaction(
            user_id=data['user_id'],
            emotion_type=data['emotion_type'],
            correct=data['correct'],
            context=data.get('context'),
            trigger=data.get('trigger'),
            intensity=data.get('intensity'),
            notes=data.get('notes')
        )
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 400
            
        return jsonify({'success': True, 'data': result}), 200
        
    except Exception as e:
        logger.error(f"Error in record_emotion_interaction route: {str(e)}")
        return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500


@emotion_progress_bp.route('/learning-path/update', methods=['POST'])
def update_learning_path_progress():
    """
    Update a user's progress on a learning path step
    
    Expected request body:
    {
        "user_id": 1,
        "path_id": 1,
        "step_id": 2,
        "progress_percentage": 75.5,
        "is_completed": false
    }
    
    Returns:
        JSON with update results
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        required_fields = ['user_id', 'path_id', 'step_id', 'progress_percentage']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Process the update
        result = EmotionProgressService.update_learning_path_progress(
            user_id=data['user_id'],
            path_id=data['path_id'],
            step_id=data['step_id'],
            progress_percentage=data['progress_percentage'],
            is_completed=data.get('is_completed', False)
        )
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 400
            
        return jsonify({'success': True, 'data': result}), 200
        
    except Exception as e:
        logger.error(f"Error in update_learning_path_progress route: {str(e)}")
        return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500


@emotion_progress_bp.route('/achievements/<int:user_id>', methods=['GET'])
def get_user_achievements(user_id: int):
    """
    Get all achievements for a user
    
    Args:
        user_id: ID of the user
        
    Returns:
        JSON with earned and available achievements
    """
    try:
        result = EmotionProgressService.get_user_achievements(user_id)
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 400
            
        return jsonify({'success': True, 'data': result}), 200
        
    except Exception as e:
        logger.error(f"Error in get_user_achievements route: {str(e)}")
        return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500


@emotion_progress_bp.route('/info/emotion-types', methods=['GET'])
def get_emotion_types():
    """
    Get all available emotion types
    
    Returns:
        JSON with emotion type information
    """
    try:
        emotion_types = [
            {
                'id': emotion.value,
                'name': emotion.name.capitalize(),
                'description': get_emotion_description(emotion)
            }
            for emotion in EmotionType
        ]
        
        return jsonify({
            'success': True, 
            'data': emotion_types
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_emotion_types route: {str(e)}")
        return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500


@emotion_progress_bp.route('/info/progress-levels', methods=['GET'])
def get_progress_levels():
    """
    Get all available progress levels
    
    Returns:
        JSON with progress level information
    """
    try:
        progress_levels = [
            {
                'id': level.value,
                'name': level.name.capitalize(),
                'description': get_level_description(level)
            }
            for level in ProgressLevel
        ]
        
        return jsonify({
            'success': True, 
            'data': progress_levels
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_progress_levels route: {str(e)}")
        return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500


# Helper functions
def get_emotion_description(emotion_type: EmotionType) -> str:
    """Get a description for an emotion type"""
    descriptions = {
        EmotionType.HAPPINESS: "Joy, pleasure, or contentment associated with positive experiences.",
        EmotionType.SADNESS: "Feelings of loss, disappointment, or disconnection.",
        EmotionType.ANGER: "Strong feelings of displeasure, hostility, or antagonism.",
        EmotionType.FEAR: "Response to perceived danger or threat, causing anxiety or apprehension.",
        EmotionType.SURPRISE: "Sudden feeling of wonder or astonishment from unexpected events.",
        EmotionType.DISGUST: "Strong aversion or repulsion triggered by something offensive.",
        EmotionType.MIXED: "Complex emotions that blend multiple feelings simultaneously."
    }
    
    return descriptions.get(emotion_type, "No description available")


def get_level_description(level: ProgressLevel) -> str:
    """Get a description for a progress level"""
    descriptions = {
        ProgressLevel.NOVICE: "Beginning stage of emotional awareness with basic recognition skills.",
        ProgressLevel.BEGINNER: "Developing consistent ability to identify and name emotions.",
        ProgressLevel.INTERMEDIATE: "Connecting emotions to their triggers and understanding patterns.",
        ProgressLevel.ADVANCED: "Skilled at recognizing subtle emotional nuances and managing responses.",
        ProgressLevel.MASTER: "Expert level of emotional intelligence with deep insights and control."
    }
    
    return descriptions.get(level, "No description available")


def register_routes(app):
    """Register routes with the Flask application"""
    app.register_blueprint(emotion_progress_bp)
    logger.info("Emotion progress routes registered")