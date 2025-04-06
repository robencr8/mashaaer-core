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
    Get context-aware personalized recommendations based on user's emotional data
    and comprehensive contextual factors.
    
    This endpoint should be accessed via POST since it analyzes user data
    and generates personalized content.
    
    Request body:
    {
        "user_id": "user123",  // Optional, will use session ID if not provided
        "emotion_data": {      // Optional current emotional state
            "primary_emotion": "joy",
            "intensity": 0.7,   // Optional intensity (0.0-1.0)
            "emotion_data": {}  // Optional detailed emotion data
        },  
        "context": {           // Optional enhanced contextual data
            "weather": {       // Optional weather context
                "condition": "sunny",
                "temperature": 25,
                "humidity": 40
            },
            "location": {      // Optional location context
                "city": "Dubai",
                "indoor": true,
                "setting": "office"
            },
            "social": {        // Optional social context
                "alone": false,
                "with_family": true,
                "event_type": "dinner"
            },
            "device": {        // Optional device context
                "type": "mobile",
                "screen_size": "medium",
                "capabilities": ["audio", "haptic"]
            }
        },
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
            "contextual_suggestions": [...],
            "engagement_activities": [...],
            "affirmation": "...",
            "current_emotion": "joy",
            "wellbeing_score": 0.75,
            "context": {
                "time_of_day": "evening",
                "day_of_week": "friday",
                "is_weekend": true,
                "season": "summer",
                "weather": { ... }
            },
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
        logger.info(f"Generating context-aware recommendations for user: {user_id}")
        
        # Extract other parameters
        emotion_data = data.get('emotion_data')
        context = data.get('context', {})
        force_refresh = data.get('force_refresh', False)
        
        # Add enhanced location-based context if available
        if context and 'location' in context:
            location = context.get('location', {})
            city = location.get('city')
            if city:
                # In a production environment, we would fetch real weather data here
                # based on the location, or use geolocation services to enhance context
                pass
                
        # Generate a unique recommendation ID
        recommendation_id = f"rec_{uuid4().hex[:12]}"
        
        # Get context-aware recommendations
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
        logger.error(f"Error generating context-aware recommendations: {str(e)}")
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


@recommendation_bp.route('/greeting', methods=['GET'])
def get_contextual_greeting():
    """
    Get a time-appropriate contextual greeting
    
    Query parameters:
    - language: Language code ('en' or 'ar'), defaults to 'en'
    
    Returns:
    {
        "success": true,
        "greeting": "Good morning! Ready for a bright weekday?"
    }
    """
    try:
        language = request.args.get('language', 'en')
        if language not in ['en', 'ar']:
            language = 'en'  # Default to English for unsupported languages
            
        greeting = recommendation_engine.get_contextual_greeting(language)
        
        return jsonify({
            'success': True,
            'greeting': greeting
        })
        
    except Exception as e:
        logger.error(f"Error generating contextual greeting: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate greeting',
            'message': str(e)
        }), 500


@recommendation_bp.route('/contextual', methods=['POST'])
def get_contextual_recommendations():
    """
    Get highly specific recommendations for a particular context, event, or activity
    
    This endpoint provides deeply contextualized recommendations for specific situations,
    whether that's a stressful work meeting, family gathering, creative block, etc.
    
    Request body:
    {
        "user_id": "user123",  // Optional, will use session ID if not provided
        "emotion_data": {      // Optional current emotional state
            "primary_emotion": "anxiety",
            "intensity": 0.8,
            "emotion_data": {}  
        },
        "context_type": "event" | "activity" | "situation",
        "context_details": {
            "type": "work_meeting" | "family_gathering" | "creative_session" | "conflict" | "decision",
            "description": "Preparing for an important presentation to senior management",
            "urgency": "immediate" | "today" | "this_week",  // Optional timing context
            "importance": 0.9,  // Optional importance level (0.0-1.0)
            "location": "office" | "home" | "public",  // Optional location context
            "social_setting": "alone" | "small_group" | "large_group"  // Optional social context
        }
    }
    
    Returns:
    {
        "success": true,
        "contextual_recommendations": {
            "before": [...],  // Recommendations for before the event/activity
            "during": [...],  // Recommendations for during the event/activity
            "after": [...],   // Recommendations for after the event/activity
            "emotional_regulation": [...],  // Specific emotional regulation techniques
            "perspective_shifts": [...],   // Ways to reframe or view the situation
            "reflection_prompts": [...]    // Questions to consider about the situation
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
            
        # Get context details
        emotion_data = data.get('emotion_data')
        context_type = data.get('context_type')
        context_details = data.get('context_details', {})
        
        # Validate required fields
        if not context_type or not context_details:
            return jsonify({
                'success': False,
                'error': 'Missing context information'
            }), 400
            
        # Generate a unique recommendation ID
        recommendation_id = f"rec_contextual_{uuid4().hex[:10]}"
        
        # Prepare the context for the AI
        enhanced_context = {
            "context_type": context_type,
            "details": context_details,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Get contextual recommendations using the recommendation engine
        recommendations = recommendation_engine.get_recommendations(
            user_id=user_id,
            emotion_data=emotion_data,
            context=enhanced_context,
            force_refresh=True  # Always fresh for contextual recommendations
        )
        
        # Add the recommendation ID
        recommendations['recommendation_id'] = recommendation_id
        
        # Log the interaction
        _log_recommendation_interaction(
            user_id, 
            recommendation_id, 
            "contextual_generated",
            {
                "context_type": context_type,
                "context_summary": context_details.get("description", "")
            }
        )
        
        return jsonify({
            'success': True,
            'contextual_recommendations': recommendations
        })
        
    except Exception as e:
        logger.error(f"Error generating contextual recommendations: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate contextual recommendations',
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
        recommendation_engine.db_manager.execute_query(query, params)
        
        logger.info(f"Logged {interaction_type} interaction for recommendation {recommendation_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error logging recommendation interaction: {str(e)}")
        return False