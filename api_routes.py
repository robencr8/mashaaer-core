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
from rules_config_loader import RulesConfigLoader, load_rules_from_config
from rule_engine import RobinDecisionEngine, Rule
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

# Initialize rules config loader and Robin Decision Engine
rules_loader = RulesConfigLoader()
robin_engine = load_rules_from_config('rules_config.json')

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
        
        # Store any user-specific data in the engine memory
        if user_id != 'anonymous':
            # Save user_id and language preference in memory for future interactions
            robin_engine.store_memory(user_id, 'language', language)
            
            # Get user's name from memory if available
            user_name = get_memory(user_id, 'name')
            if user_name:
                robin_engine.store_memory(user_id, 'name', user_name)
        
        # Use RobinDecisionEngine to decide the appropriate action
        decision = robin_engine.decide(message, emotion)
        
        action = decision.get('action', 'respond_normally')
        params = decision.get('params', {})
        
        # For compatibility with the existing system, also check rules_loader
        # to get the rule_id that matched
        matched_rules = rules_loader.match_rules(emotion, message, language)
        rule_id = matched_rules[0].get('id') if matched_rules else None
        
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
        
        # Calculate delta for rule weight adjustment
        delta = 0.1 if feedback.lower() == 'positive' else -0.1
        
        # Adjust rule weight in both systems
        rules_success = rules_loader.adjust_rule_weight(rule_id, feedback)
        engine_success = robin_engine.update_rule_weight(rule_id, delta)
        
        if not rules_success and not engine_success:
            return jsonify({
                'success': False, 
                'error': f'Failed to process feedback for rule ID: {rule_id}. Rule not found in any system.'
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
        
        # Add rule to rules_loader
        config_success = rules_loader.add_rule(data)
        
        # Also add rule to robin_engine
        engine_success = False
        try:
            # Create a Rule object from the data
            rule = Rule(
                emotion=data.get('emotion', 'neutral'),
                keyword=data.get('keyword', ''),
                action=data.get('action', 'respond_normally'),
                params=data.get('params', {}),
                weight=data.get('weight', 1.0),
                description=data.get('description', ''),
                rule_id=data.get('id'),
                lang=data.get('lang', 'en')
            )
            
            # Add the rule to the engine
            robin_engine.add_rule(rule)
            engine_success = True
            
        except Exception as e:
            logger.error(f"Error adding rule to RobinDecisionEngine: {str(e)}")
            
        if not config_success and not engine_success:
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
        
        # Update rule in rules_loader
        config_success = rules_loader.update_rule(rule_id, data)
        
        # Also update rule in robin_engine
        engine_success = False
        try:
            # First, remove the old rule
            robin_engine.remove_rule(rule_id)
            
            # Then create and add the new rule with updated data
            rule = Rule(
                emotion=data.get('emotion', 'neutral'),
                keyword=data.get('keyword', ''),
                action=data.get('action', 'respond_normally'),
                params=data.get('params', {}),
                weight=data.get('weight', 1.0),
                description=data.get('description', ''),
                rule_id=rule_id,  # Use the original rule_id
                lang=data.get('lang', 'en')
            )
            
            # Add the updated rule to the engine
            robin_engine.add_rule(rule)
            engine_success = True
            
        except Exception as e:
            logger.error(f"Error updating rule in RobinDecisionEngine: {str(e)}")
        
        if not config_success and not engine_success:
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
        # Delete rule from both systems
        config_success = rules_loader.delete_rule(rule_id)
        
        # Also remove from robin_engine if present
        engine_success = False
        try:
            robin_engine.remove_rule(rule_id)
            engine_success = True
        except Exception as e:
            logger.error(f"Error removing rule from RobinDecisionEngine: {str(e)}")
            
        if not config_success and not engine_success:
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
                
        elif action == 'suggest_rest':
            rest_duration = params.get('rest_duration', 20)
            return f"أرى أنك تشعر بالإرهاق يا {user_name}. أخذ استراحة قصيرة لمدة {rest_duration} دقيقة يمكن أن يساعد في استعادة طاقتك. هل تريد مني تعيين تذكير لطيف؟"
        
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
                
        elif action == 'suggest_rest':
            rest_duration = params.get('rest_duration', 20)
            return f"I can see you're feeling exhausted, {user_name}. Taking a short {rest_duration}-minute break can help restore your energy. Would you like me to set a gentle reminder?"
        
        # Default English response
        return f"I understand how you're feeling. Is there anything specific you'd like to talk about, {user_name}?"