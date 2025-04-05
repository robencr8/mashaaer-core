"""
API Routes for Mashaaer Feelings Application
Handles chat, feedback, and other API endpoints
"""
from flask import Blueprint, request, jsonify, current_app, Flask
import logging
from datetime import datetime
import os
from typing import Dict, Any, List, Optional
from textblob import TextBlob

# Import decision engine components
from rules_config_loader import RulesConfigLoader
from memory_store import save_memory, get_memory
from log_manager import log_interaction

# Set up logging
logger = logging.getLogger(__name__)

# Create Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

def detect_emotion_from_text(text):
    """
    Detect emotion from text using TextBlob sentiment analysis
    Returns: "happy", "sad", or "neutral" based on polarity
    """
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.3:
        return "happy"
    elif polarity < -0.3:
        return "sad"
    return "neutral"

def init_api(app, db_manager=None, emotion_tracker=None, face_detector=None, 
            tts_manager=None, voice_recognition=None, intent_classifier=None, config=None,
            context_assistant=None, model_router=None):
    """Initialize the API blueprint with necessary dependencies"""
    # Register the blueprint
    app.register_blueprint(api_bp)
    logger.info("API routes registered successfully")
    return api_bp

# Initialize rules config loader
rules_loader = RulesConfigLoader()

@api_bp.route('/chat', methods=['POST'])
def chat():
    """
    Process chat messages with emotion-based decision rules
    
    Request body:
    {
        "message": "I feel alone today",
        "emotion": "sad" (optional - auto-detected if not provided),
        "user_id": "user123" (optional),
        "lang": "en" or "ar" (optional - defaults to "en")
    }
    
    Returns:
    {
        "success": true,
        "action": "offer_companionship",
        "response": "I'm here for you...",
        "rule_matched": "rule001",
        "detected_emotion": "sad",
        "params": {} (optional)
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Extract required fields
        message = data.get('message')
        language = data.get('lang', 'en')  # Default language is English
        user_id = data.get('user_id', 'anonymous')
        
        if not message:
            return jsonify({
                'success': False, 
                'error': 'Missing required field: message'
            }), 400
        
        # Auto-detect emotion if not provided
        emotion = data.get('emotion')
        if not emotion:
            emotion = detect_emotion_from_text(message)
            logger.info(f"Auto-detected emotion '{emotion}' for message: '{message}'")
        
        # Match rules based on emotion, language and message
        matched_rules = rules_loader.match_rules(emotion, message, language)
        
        if not matched_rules:
            # No rules matched, return default response
            response = {
                'success': True,
                'action': 'default_response',
                'response': 'I understand. Tell me more about how you feel.',
                'rule_matched': None,
                'detected_emotion': emotion
            }
        else:
            # Use the highest weighted matching rule
            best_match = matched_rules[0]
            
            # Get action and parameters
            action = best_match.get('action')
            params = best_match.get('params', {})
            rule_id = best_match.get('id')
            
            # Generate response based on action
            response_text = generate_response(action, params, emotion, user_id, language)
            
            response = {
                'success': True,
                'action': action,
                'response': response_text,
                'rule_matched': rule_id,
                'detected_emotion': emotion,
                'params': params
            }
        
        # Log the interaction
        log_interaction(message, emotion, response.get('action'), response.get('params', {}), language)
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process chat',
            'message': str(e)
        }), 500

@api_bp.route('/feedback', methods=['POST'])
def process_feedback():
    """
    Process feedback on rule effectiveness
    
    Request body:
    {
        "rule_id": "rule001",
        "feedback": "positive" | "negative"
    }
    
    Returns:
    {
        "success": true,
        "message": "Feedback processed successfully",
        "new_weight": 1.1
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Extract required fields
        rule_id = data.get('rule_id')
        feedback = data.get('feedback')
        
        if not rule_id or not feedback:
            return jsonify({
                'success': False, 
                'error': 'Missing required fields: rule_id and feedback'
            }), 400
        
        # Validate feedback value
        if feedback.lower() not in ['positive', 'negative']:
            return jsonify({
                'success': False, 
                'error': 'Invalid feedback value. Must be "positive" or "negative"'
            }), 400
        
        # Adjust rule weight based on feedback
        success = rules_loader.adjust_rule_weight(rule_id, feedback)
        
        if not success:
            return jsonify({
                'success': False, 
                'error': f'Failed to process feedback for rule ID: {rule_id}'
            }), 404
        
        # Get updated rule for response
        updated_rule = rules_loader.get_rule_by_id(rule_id)
        
        return jsonify({
            'success': True,
            'message': 'Feedback processed successfully',
            'new_weight': updated_rule.get('weight')
        })
    
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process feedback',
            'message': str(e)
        }), 500

@api_bp.route('/rules', methods=['GET'])
def get_rules():
    """
    Get all configured rules
    
    Returns:
    {
        "success": true,
        "rules": [
            {
                "id": "rule001",
                "emotion": "sad",
                "keyword": "alone",
                "action": "offer_companionship",
                "weight": 1.0
            },
            ...
        ]
    }
    """
    try:
        rules = rules_loader.get_rules()
        
        return jsonify({
            'success': True,
            'rules': rules
        })
    
    except Exception as e:
        logger.error(f"Error getting rules: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get rules',
            'message': str(e)
        }), 500

@api_bp.route('/rules/<rule_id>', methods=['GET'])
def get_rule(rule_id):
    """
    Get a specific rule by ID
    
    Returns:
    {
        "success": true,
        "rule": {
            "id": "rule001",
            "emotion": "sad",
            "keyword": "alone",
            "action": "offer_companionship",
            "weight": 1.0
        }
    }
    """
    try:
        rule = rules_loader.get_rule_by_id(rule_id)
        
        if not rule:
            return jsonify({
                'success': False, 
                'error': f'Rule not found for ID: {rule_id}'
            }), 404
        
        return jsonify({
            'success': True,
            'rule': rule
        })
    
    except Exception as e:
        logger.error(f"Error getting rule: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get rule',
            'message': str(e)
        }), 500

@api_bp.route('/rules', methods=['POST'])
def add_rule():
    """
    Add a new rule
    
    Request body:
    {
        "id": "rule004",
        "emotion": "angry",
        "keyword": "frustrated",
        "action": "suggest_calming",
        "weight": 1.0,
        "params": {
            "technique": "breathing"
        }
    }
    
    Returns:
    {
        "success": true,
        "message": "Rule added successfully",
        "rule": {
            "id": "rule004",
            "emotion": "angry",
            "keyword": "frustrated",
            "action": "suggest_calming",
            "weight": 1.0,
            "params": {
                "technique": "breathing"
            }
        }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['id', 'emotion', 'keyword', 'action']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False, 
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Add rule
        success = rules_loader.add_rule(data)
        
        if not success:
            return jsonify({
                'success': False, 
                'error': 'Failed to add rule. Rule ID may already exist.'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Rule added successfully',
            'rule': data
        })
    
    except Exception as e:
        logger.error(f"Error adding rule: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to add rule',
            'message': str(e)
        }), 500

@api_bp.route('/rules/<rule_id>', methods=['PUT'])
def update_rule(rule_id):
    """
    Update an existing rule
    
    Request body:
    {
        "emotion": "angry",
        "keyword": "frustrated",
        "action": "suggest_calming",
        "weight": 1.2,
        "params": {
            "technique": "breathing"
        }
    }
    
    Returns:
    {
        "success": true,
        "message": "Rule updated successfully",
        "rule": {
            "id": "rule004",
            "emotion": "angry",
            "keyword": "frustrated",
            "action": "suggest_calming",
            "weight": 1.2,
            "params": {
                "technique": "breathing"
            }
        }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Update rule
        success = rules_loader.update_rule(rule_id, data)
        
        if not success:
            return jsonify({
                'success': False, 
                'error': f'Failed to update rule. Rule ID {rule_id} may not exist.'
            }), 404
        
        # Get updated rule
        updated_rule = rules_loader.get_rule_by_id(rule_id)
        
        return jsonify({
            'success': True,
            'message': 'Rule updated successfully',
            'rule': updated_rule
        })
    
    except Exception as e:
        logger.error(f"Error updating rule: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update rule',
            'message': str(e)
        }), 500

@api_bp.route('/rules/<rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    """
    Delete a rule
    
    Returns:
    {
        "success": true,
        "message": "Rule deleted successfully"
    }
    """
    try:
        # Delete rule
        success = rules_loader.delete_rule(rule_id)
        
        if not success:
            return jsonify({
                'success': False, 
                'error': f'Failed to delete rule. Rule ID {rule_id} may not exist.'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Rule deleted successfully'
        })
    
    except Exception as e:
        logger.error(f"Error deleting rule: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete rule',
            'message': str(e)
        }), 500

@api_bp.route('/memory', methods=['POST'])
def set_memory():
    """
    Save user memory
    
    Request body:
    {
        "user_id": "user123",
        "key": "preferred_activity",
        "value": "meditation"
    }
    
    Returns:
    {
        "success": true,
        "message": "Memory saved successfully"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Extract required fields
        user_id = data.get('user_id')
        key = data.get('key')
        value = data.get('value')
        
        if not user_id or not key or value is None:
            return jsonify({
                'success': False, 
                'error': 'Missing required fields: user_id, key, and value'
            }), 400
        
        # Save memory
        save_memory(user_id, key, value)
        
        return jsonify({
            'success': True,
            'message': 'Memory saved successfully'
        })
    
    except Exception as e:
        logger.error(f"Error saving memory: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to save memory',
            'message': str(e)
        }), 500

@api_bp.route('/memory/<user_id>/<key>', methods=['GET'])
def get_user_memory(user_id, key):
    """
    Get user memory
    
    Returns:
    {
        "success": true,
        "key": "preferred_activity",
        "value": "meditation"
    }
    """
    try:
        # Get memory
        value = get_memory(user_id, key)
        
        if value is None:
            return jsonify({
                'success': False, 
                'error': f'Memory not found for user {user_id} and key {key}'
            }), 404
        
        return jsonify({
            'success': True,
            'key': key,
            'value': value
        })
    
    except Exception as e:
        logger.error(f"Error getting memory: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get memory',
            'message': str(e)
        }), 500

def generate_response(action: str, params: Dict[str, Any], emotion: str, user_id: str, language: str = 'en') -> str:
    """
    Generate a response based on the action and parameters
    
    Args:
        action: The action to perform
        params: Additional parameters for the action
        emotion: The detected emotion
        user_id: The user's ID for personalization
        language: The language to respond in ('en' or 'ar')
    
    Returns:
        A response string in the appropriate language
    """
    # Get user preferences from memory if available
    user_name = get_memory(user_id, 'name') or "there"
    
    # Choose response based on language and action
    if language == 'ar':
        # Arabic responses
        if action == 'offer_companionship':
            return f"مرحبًا {user_name}، أنا هنا من أجلك. أنت لست وحيدًا، وأنا سعيد بمرافقتك عندما تحتاج إلى شخص للتحدث معه."
        
        elif action == 'play_music':
            genre = params.get('genre', 'هادئة')
            return f"أعتقد أن بعض الموسيقى {genre} قد تساعد في رفع معنوياتك. هل تريد أن أقترح عليك بعض المقطوعات؟"
        
        elif action == 'fetch_weather':
            return f"هل ترغب في معرفة توقعات الطقس اليوم؟ يمكنني التحقق من ذلك لك على الفور."
        
        elif action == 'suggest_calming':
            technique = params.get('technique', 'التنفس')
            if technique == 'التنفس' or technique == 'breathing':
                return f"ألاحظ أنك تبدو محبطًا. هل سيساعدك تجربة تمرين تنفس سريع معي؟ تنفس للداخل لمدة 4 عدات، وللخارج لمدة 6 عدات."
            else:
                return f"عندما تشعر بهذه الطريقة، أخذ لحظة لنفسك قد يساعد. هل ترغب في تجربة تمرين {technique} سريع؟"
        
        # Default Arabic response
        return f"أفهم شعورك. هل هناك شيء محدد ترغب في التحدث عنه يا {user_name}؟"
    
    else:
        # English responses (default)
        if action == 'offer_companionship':
            return f"Hi {user_name}, I'm here for you. You're not alone, and I'm happy to keep you company whenever you need someone to talk to."
        
        elif action == 'play_music':
            genre = params.get('genre', 'relaxing')
            return f"I think some {genre} music might help lift your spirits. Would you like me to suggest some tracks?"
        
        elif action == 'fetch_weather':
            return f"Would you like to know today's weather forecast? I can check that for you right away."
        
        elif action == 'suggest_calming':
            technique = params.get('technique', 'breathing')
            if technique == 'breathing':
                return f"I notice you seem frustrated. Would it help to try a quick breathing exercise with me? Breathe in for 4 counts, and out for 6 counts."
            else:
                return f"When you're feeling this way, taking a moment for yourself can help. Would you like to try a quick {technique} exercise?"
        
        # Default English response
        return f"I understand how you're feeling. Is there anything specific you'd like to talk about, {user_name}?"