"""
Recommendation Engine API Routes

This module provides routes for accessing the recommendation engine
and retrieving personalized suggestions for users.
"""

import logging
import json
from datetime import datetime
from uuid import uuid4
from flask import Blueprint, request, jsonify, session
from recommendation_engine import RecommendationEngine

# Configure logging
logger = logging.getLogger(__name__)

# Create the blueprint
recommendation_bp = Blueprint('recommendation', __name__)

# Global recommendation engine instance
recommendation_engine = None


def init_recommendation_api(app, _db_manager, _emotion_tracker):
    """Initialize the recommendation API blueprint with necessary dependencies"""
    global recommendation_engine
    
    # Initialize the recommendation engine
    if not recommendation_engine:
        recommendation_engine = RecommendationEngine(_db_manager, _emotion_tracker)
        
        # Create necessary database tables
        recommendation_engine.create_tables()
    
    # Register the blueprint with the app
    app.register_blueprint(recommendation_bp, url_prefix='/api/recommendations')
    
    logger.info("Recommendation API routes registered successfully")
    return app


@recommendation_bp.route('/get', methods=['POST'])
def get_recommendations():
    """
    Get personalized recommendations based on user's emotional data
    
    This endpoint should be accessed via POST since it analyzes user data
    and generates personalized content.
    
    Request body:
    {
        "user_id": "user123",  // Optional, will use session ID if not provided
        "emotion_data": {...},  // Optional current emotional state
        "context": {...},      // Optional additional context
        "force_refresh": false  // Optional, force regeneration of recommendations
    }
    
    Returns:
    {
        "success": true,
        "recommendations": {
            "immediate_actions": [...],
            "wellbeing_practices": [...],
            "social_connections": [...],
            "creative_expression": [...],
            "reflective_insights": [...],
            "affirmation": "...",
            "current_emotion": "joy",
            "wellbeing_score": 0.75,
            "generated_at": "2025-04-05T12:34:56"
        },
        "recommendation_id": "rec_123abc"
    }
    """
    try:
        # Get request data
        data = request.get_json() or {}
        
        # Get user ID (from request or session)
        user_id = data.get('user_id')
        if not user_id:
            user_id = session.get('user_id', f"anonymous_{uuid4().hex[:8]}")
            
        # Log the request
        logger.info(f"Generating recommendations for user: {user_id}")
        
        # Extract other parameters
        emotion_data = data.get('emotion_data')
        context = data.get('context')
        force_refresh = data.get('force_refresh', False)
        
        # Generate a unique recommendation ID
        recommendation_id = f"rec_{uuid4().hex[:12]}"
        
        # Get recommendations
        recommendations = recommendation_engine.get_recommendations(
            user_id=user_id,
            emotion_data=emotion_data,
            context=context,
            force_refresh=force_refresh
        )
        
        # Store the recommendation ID in the recommendations
        recommendations['recommendation_id'] = recommendation_id
        
        # Log the interaction
        _log_recommendation_interaction(user_id, recommendation_id, "generated")
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'recommendation_id': recommendation_id
        })
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate recommendations',
            'message': str(e)
        }), 500


@recommendation_bp.route('/feedback', methods=['POST'])
def submit_recommendation_feedback():
    """
    Submit feedback on recommendations
    
    This endpoint should be accessed via POST since it submits user feedback.
    
    Request body:
    {
        "user_id": "user123",  // Optional, will use session ID if not provided
        "recommendation_id": "rec_123abc",
        "feedback": {
            "helpful": true,
            "implemented": ["immediate_actions.0", "wellbeing_practices.1"],
            "rating": 4,  // Optional rating (1-5)
            "comments": "..."  // Optional comments
        }
    }
    
    Returns:
    {
        "success": true,
        "message": "Feedback submitted successfully"
    }
    """
    try:
        # Get request data
        data = request.get_json() or {}
        
        # Get user ID (from request or session)
        user_id = data.get('user_id')
        if not user_id:
            user_id = session.get('user_id', f"anonymous_{uuid4().hex[:8]}")
            
        # Get recommendation ID and feedback
        recommendation_id = data.get('recommendation_id')
        feedback = data.get('feedback', {})
        
        # Validate required fields
        if not recommendation_id:
            return jsonify({
                'success': False,
                'error': 'Missing recommendation_id'
            }), 400
            
        if not feedback:
            return jsonify({
                'success': False,
                'error': 'Missing feedback data'
            }), 400
        
        # Log the feedback
        success = recommendation_engine.log_recommendation_feedback(
            user_id=user_id,
            recommendation_id=recommendation_id,
            feedback=feedback
        )
        
        # Log the interaction
        _log_recommendation_interaction(
            user_id, 
            recommendation_id, 
            "feedback",
            {
                "helpful": feedback.get("helpful"),
                "rating": feedback.get("rating")
            }
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Feedback submitted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to submit feedback'
            }), 500
            
    except Exception as e:
        logger.error(f"Error submitting recommendation feedback: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to submit feedback',
            'message': str(e)
        }), 500


@recommendation_bp.route('/interaction', methods=['POST'])
def log_recommendation_interaction():
    """
    Log an interaction with a recommendation
    
    This endpoint should be accessed via POST since it logs user activity.
    
    Request body:
    {
        "user_id": "user123",  // Optional, will use session ID if not provided
        "recommendation_id": "rec_123abc",
        "interaction_type": "viewed",  // viewed, clicked, implemented, etc.
        "details": {...}  // Optional details about the interaction
    }
    
    Returns:
    {
        "success": true,
        "message": "Interaction logged successfully"
    }
    """
    try:
        # Get request data
        data = request.get_json() or {}
        
        # Get user ID (from request or session)
        user_id = data.get('user_id')
        if not user_id:
            user_id = session.get('user_id', f"anonymous_{uuid4().hex[:8]}")
            
        # Get recommendation ID and interaction details
        recommendation_id = data.get('recommendation_id')
        interaction_type = data.get('interaction_type')
        details = data.get('details', {})
        
        # Validate required fields
        if not recommendation_id:
            return jsonify({
                'success': False,
                'error': 'Missing recommendation_id'
            }), 400
            
        if not interaction_type:
            return jsonify({
                'success': False,
                'error': 'Missing interaction_type'
            }), 400
        
        # Log the interaction
        success = _log_recommendation_interaction(
            user_id=user_id,
            recommendation_id=recommendation_id,
            interaction_type=interaction_type,
            details=details
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Interaction logged successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to log interaction'
            }), 500
            
    except Exception as e:
        logger.error(f"Error logging recommendation interaction: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to log interaction',
            'message': str(e)
        }), 500


def _log_recommendation_interaction(user_id, recommendation_id, interaction_type, details=None):
    """
    Log an interaction with a recommendation to the database
    
    Args:
        user_id: User identifier
        recommendation_id: Recommendation identifier
        interaction_type: Type of interaction (viewed, clicked, implemented, etc.)
        details: Optional details about the interaction
        
    Returns:
        Boolean indicating success
    """
    try:
        if not recommendation_engine or not recommendation_engine.db_manager:
            logger.error("Recommendation engine or DB manager not initialized")
            return False
            
        # Convert details to JSON string
        details_json = json.dumps(details) if details else None
        timestamp = datetime.now().isoformat()
        
        # Insert into database
        query = """
        INSERT INTO recommendation_interactions 
        (user_id, recommendation_id, interaction_type, details, timestamp) 
        VALUES (?, ?, ?, ?, ?)
        """
        
        params = (user_id, recommendation_id, interaction_type, details_json, timestamp)
        recommendation_engine.db_manager.execute_query(query, params, fetch=False)
        
        logger.info(f"Logged {interaction_type} interaction for recommendation {recommendation_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error logging recommendation interaction: {str(e)}")
        return False