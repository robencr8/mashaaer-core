import os
import json
import time
import uuid
import logging
import traceback
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, session

# Setup logging
logger = logging.getLogger(__name__)

# Blueprint definition
api = Blueprint('api', __name__)

# Global references (will be set when registered with app)
db_manager = None
emotion_tracker = None
face_detector = None
tts_manager = None
voice_recognition = None
intent_classifier = None
config = None
model_router = None  # AI Model Router reference
context_assistant = None  # Reference to context assistant for AI capabilities

def init_api(app, _db_manager, _emotion_tracker, _face_detector, 
            _tts_manager, _voice_recognition, _intent_classifier, _config,
            _context_assistant=None, _model_router=None):
    """Initialize the API blueprint with necessary dependencies"""
    global db_manager, emotion_tracker, face_detector, tts_manager
    global voice_recognition, intent_classifier, config, context_assistant, model_router
    
    # Store references to core components
    db_manager = _db_manager
    emotion_tracker = _emotion_tracker
    face_detector = _face_detector
    tts_manager = _tts_manager
    voice_recognition = _voice_recognition
    intent_classifier = _intent_classifier
    config = _config
    context_assistant = _context_assistant
    
    # Initialize model router if not provided
    if _model_router:
        model_router = _model_router
    elif context_assistant and hasattr(context_assistant, 'model_router'):
        model_router = context_assistant.model_router
    else:
        # Create AI Model Router on demand if not available
        try:
            from ai_model_router import AIModelRouter
            model_router = AIModelRouter()
            logger.info("Initialized AI Model Router for API routes")
        except Exception as e:
            logger.warning(f"Could not initialize AI Model Router: {str(e)}")
            model_router = None
    
    # Add API documentation endpoint
    @api.route('/', methods=['GET'])
    def api_docs():
        """API documentation listing all available endpoints"""
        endpoints = {
            '/api/status': {
                'methods': ['GET'],
                'description': 'Get system status and information about all subsystems',
                'params': []
            },
            '/api/emotion-data': {
                'methods': ['GET'],
                'description': 'Get emotion data for visualization',
                'params': [
                    {'name': 'days', 'type': 'int', 'default': 7, 'description': 'Number of days of data to retrieve'},
                    {'name': 'session_only', 'type': 'bool', 'default': False, 'description': 'Only get data for current session'},
                    {'name': 'session_id', 'type': 'string', 'default': None, 'description': 'Get data for specific session ID'}
                ]
            },
            '/api/face-recognition-data': {
                'methods': ['GET'],
                'description': 'Get face recognition data',
                'params': [
                    {'name': 'limit', 'type': 'int', 'default': 20, 'description': 'Number of records to retrieve'},
                    {'name': 'session_only', 'type': 'bool', 'default': False, 'description': 'Only get data for current session'}
                ]
            },
            '/api/recent-conversations': {
                'methods': ['GET'],
                'description': 'Get recent conversation history',
                'params': [
                    {'name': 'limit', 'type': 'int', 'default': 10, 'description': 'Number of conversations to retrieve'},
                    {'name': 'session_only', 'type': 'bool', 'default': False, 'description': 'Only get conversations for current session'}
                ]
            },
            '/api/voice-logs': {
                'methods': ['GET'],
                'description': 'Get voice recognition logs',
                'params': [
                    {'name': 'limit', 'type': 'int', 'default': 20, 'description': 'Number of logs to retrieve'},
                    {'name': 'session_only', 'type': 'bool', 'default': False, 'description': 'Only get logs for current session'}
                ]
            },
            '/api/profiles': {
                'methods': ['GET'],
                'description': 'Get all saved face profiles with metadata',
                'params': []
            },
            '/api/profile/<name>': {
                'methods': ['GET'],
                'description': 'Get a specific profile by name',
                'params': [
                    {'name': 'name', 'type': 'string', 'required': True, 'description': 'Profile name to retrieve'}
                ]
            },
            '/api/log-recognition': {
                'methods': ['POST'],
                'description': 'Log a face recognition event',
                'params': [
                    {'name': 'name', 'type': 'string', 'required': True, 'description': 'Name of recognized person'},
                    {'name': 'confidence', 'type': 'float', 'default': 0.0, 'description': 'Recognition confidence'},
                    {'name': 'emotion', 'type': 'string', 'default': 'neutral', 'description': 'Detected emotion'},
                    {'name': 'greeting', 'type': 'string', 'default': None, 'description': 'Greeting message used'}
                ]
            },
            '/api/log-emotion': {
                'methods': ['POST'],
                'description': 'Log an emotion detection event',
                'params': [
                    {'name': 'emotion', 'type': 'string', 'required': True, 'description': 'Detected emotion'},
                    {'name': 'text', 'type': 'string', 'default': '', 'description': 'Text content'},
                    {'name': 'source', 'type': 'string', 'default': 'text', 'description': 'Source of emotion (text, voice, face)'},
                    {'name': 'intensity', 'type': 'float', 'default': 0.5, 'description': 'Emotion intensity (0-1)'}
                ]
            },
            '/api/retrain-emotion-model': {
                'methods': ['POST'],
                'description': 'Trigger emotion model retraining (requires developer mode)',
                'params': []
            },
            '/api/sessions': {
                'methods': ['GET'],
                'description': 'Get a list of available sessions',
                'params': [
                    {'name': 'limit', 'type': 'int', 'default': 10, 'description': 'Number of sessions to retrieve'}
                ]
            },
            '/api/sms': {
                'methods': ['POST'],
                'description': 'Send SMS notification via Twilio',
                'params': [
                    {'name': 'to_number', 'type': 'string', 'required': True, 'description': 'Recipient phone number in E.164 format'},
                    {'name': 'message', 'type': 'string', 'required': True, 'description': 'Message content to send'}
                ]
            },
            '/api/sms-alert': {
                'methods': ['POST'],
                'description': 'Send SMS alert notification with pre-formatted message',
                'params': [
                    {'name': 'to_number', 'type': 'string', 'required': True, 'description': 'Recipient phone number in E.164 format'},
                    {'name': 'alert_type', 'type': 'string', 'default': 'alert', 'description': 'Alert type (alert, reminder, update, emotion, face, security, system)'},
                    {'name': 'alert_data', 'type': 'object', 'required': True, 'description': 'Data for the alert message template'}
                ]
            },
            '/api/session-data': {
                'methods': ['GET'],
                'description': 'Get comprehensive data for a specific session',
                'params': [
                    {'name': 'session_id', 'type': 'string', 'default': 'current', 'description': 'Session ID to retrieve data for'}
                ]
            },
            '/api/ai-models': {
                'methods': ['GET'],
                'description': 'Get information about available AI models',
                'params': []
            },
            '/api/ai-query': {
                'methods': ['POST'],
                'description': 'Send a direct query to the selected AI model',
                'params': [
                    {'name': 'query', 'type': 'string', 'required': True, 'description': 'The text query to send to the AI model'},
                    {'name': 'model', 'type': 'string', 'default': None, 'description': 'Optional specific model to use'},
                    {'name': 'system_prompt', 'type': 'string', 'default': None, 'description': 'Optional system instructions'},
                    {'name': 'temperature', 'type': 'float', 'default': 0.7, 'description': 'Controls randomness (0.0 to 1.0)'}
                ]
            }
        }
        
        return jsonify({
            'name': 'Robin AI Enhanced API',
            'version': 'v2.0.0',
            'base_url': '/api',
            'endpoints': endpoints,
            'success': True
        })
    
    # Register the blueprint
    app.register_blueprint(api, url_prefix='/api')
    
    # Configure logging for all API requests
    @app.before_request
    def log_api_request():
        if request.path.startswith('/api/'):
            api_info = {
                'endpoint': request.path,
                'method': request.method,
                'args': {k: v for k, v in request.args.items()},
                'content_type': request.content_type,
                'has_json': request.is_json
            }
            
            # Add JSON data if available
            if request.is_json:
                try:
                    api_info['json'] = request.get_json()
                except:
                    api_info['json'] = 'Error parsing JSON'
                    
            logger.info(f"🔍 API Request: {api_info}")

# API Helper functions
def _get_or_create_session_id():
    """Get the current session ID or create a new one"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        
        # Add to sessions table
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Create session in database
        db_manager.execute_query(
            """
            INSERT INTO sessions (id, start_time, user_name, device_info, metadata)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (session['session_id'], timestamp, 'Anonymous', user_agent, json.dumps({}))
        )
    
    return session['session_id']

# API Routes

@api.route('/status', methods=['GET'])
def get_status():
    """Get system status information"""
    try:
        # Initialize response
        status = {
            'system': {
                'online': True,
                'version': '1.0.0',
                'db_size': db_manager.get_db_size(),
                'offline_mode': config.is_offline(),
                'uptime': 'Unknown'  # Will be filled by core launcher if available
            },
            'modules': {
                'emotion_tracking': emotion_tracker is not None,
                'face_detection': face_detector is not None,
                'tts': tts_manager is not None,
                'voice_recognition': voice_recognition is not None,
                'intent_classification': intent_classifier is not None
            }
        }
        
        # Notification service status
        from twilio_handler import TwilioHandler
        twilio_handler = TwilioHandler()
        status['notifications'] = {
            'provider': 'Twilio',
            'available': twilio_handler.is_available(),
            'sms_enabled': twilio_handler.is_available(),
            'phone_number': twilio_handler.phone_number[-4:] if twilio_handler.is_available() else None,
            'can_send_international': False,  # Trial accounts can't send to international numbers
            'status': 'active' if twilio_handler.is_available() else 'inactive'
        }
        
        # Current session info
        session_id = _get_or_create_session_id()
        status['session'] = {
            'id': session_id,
            'developer_mode': False  # Will be set to True if creator is detected
        }
        
        # Check for developer mode
        developer_name = os.environ.get('DEVELOPER_NAME', 'Roben Edwan')
        try:
            # Check if the developer's face was recently detected
            recent_recognitions = db_manager.execute_query(
                """
                SELECT name, timestamp FROM recognition_history 
                WHERE name = %s AND timestamp > NOW() - INTERVAL '30 minutes'
                ORDER BY timestamp DESC LIMIT 1
                """,
                (developer_name,)
            )
            
            if recent_recognitions and len(recent_recognitions) > 0:
                status['session']['developer_mode'] = True
                status['session']['developer_name'] = developer_name
                status['session']['last_seen'] = recent_recognitions[0][1]
        except Exception as e:
            logger.error(f"Error checking developer mode: {e}")
        
        return jsonify({'success': True, **status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/emotion-data', methods=['GET'])
def get_emotion_data():
    """Get emotion data for visualization"""
    try:
        # Time period (days)
        days = request.args.get('days', default=7, type=int)
        session_only = request.args.get('session_only', default=False, type=bool)
        session_id = request.args.get('session_id', None)
        cache_buster = request.args.get('_t', None)  # For cache busting
        
        # Add debug log for monitoring data requests
        logger.info(f"📊 Emotion data request: days={days}, session_only={session_only}, session_id={session_id}, cache_buster={cache_buster}")
        
        # Ensure we have a valid session ID if session_only is specified
        if session_only and not session_id:
            session_id = _get_or_create_session_id()
            logger.info(f"📊 Auto-assigned session ID: {session_id}")
            
        # Fetch emotion data based on request parameters
        try:
            if session_only and session_id:
                # Get emotions from specific session
                emotion_data = emotion_tracker.get_session_emotion_history(session_id)
                logger.info(f"📊 Fetched session emotion data: {len(emotion_data.get('timeline', []))} entries")
            elif session_only:
                # Get emotions from current session
                session_id = _get_or_create_session_id()
                emotion_data = emotion_tracker.get_session_emotion_history(session_id)
                logger.info(f"📊 Fetched current session emotion data: {len(emotion_data.get('timeline', []))} entries")
            else:
                # Get all emotions within timeframe
                emotion_data = emotion_tracker.get_emotion_history(days)
                logger.info(f"📊 Fetched historical emotion data for {days} days")
        except Exception as e:
            logger.error(f"⚠️ Error fetching emotion data: {e}")
            emotion_data = {"timeline": [], "distribution": {}}
        
        # Calculate overall distribution - handle missing data gracefully
        try:
            total_entries = emotion_tracker.get_total_entries()
        except Exception as e:
            logger.error(f"⚠️ Error getting total entries: {e}")
            total_entries = 0
        
        logger.info(f"📊 Total emotion entries: {total_entries}")
        
        # Prepare response in a standardized format for both web and mobile
        # Create a simple emotions array for mobile client
        emotions = []
        
        # Process data based on the format returned
        if 'timeline' in emotion_data:
            # Session emotion data format
            for entry in emotion_data.get('timeline', []):
                emotions.append({
                    'emotion': entry.get('emotion', 'unknown'),
                    'timestamp': entry.get('timestamp'),
                    'intensity': entry.get('intensity', 0.5),
                    'source': entry.get('source', 'text')
                })
        elif 'labels' in emotion_data and 'datasets' in emotion_data:
            # General emotion history format
            for dataset in emotion_data.get('datasets', []):
                emotion_name = dataset.get('label', 'unknown').lower()
                data_points = dataset.get('data', [])
                labels = emotion_data.get('labels', [])
                
                for i, count in enumerate(data_points):
                    if count > 0 and i < len(labels):
                        date_str = labels[i]
                        # Create entries for each count
                        for _ in range(count):
                            emotions.append({
                                'emotion': emotion_name,
                                'timestamp': date_str + 'T12:00:00',  # Noon for consistency
                                'intensity': 0.5,  # Default intensity
                                'source': 'historical'
                            })
        
        # Return standardized data for mobile client
        return jsonify({
            'emotions': emotions,
            'total_entries': total_entries,
            'days': days,
            'session_only': session_only,
            'session_id': session_id,
            'success': True
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/face-recognition-data', methods=['GET'])
def get_face_recognition_data():
    """Get face recognition data"""
    try:
        # Get recent detections
        limit = request.args.get('limit', default=20, type=int)
        session_only = request.args.get('session_only', default=False, type=bool)
        
        if session_only:
            session_id = _get_or_create_session_id()
            query = """
                SELECT name, timestamp, confidence, emotion, greeting 
                FROM recognition_history
                WHERE session_id = %s
                ORDER BY timestamp DESC LIMIT %s
            """
            params = (session_id, limit)
        else:
            query = """
                SELECT name, timestamp, confidence, emotion, greeting 
                FROM recognition_history
                ORDER BY timestamp DESC LIMIT %s
            """
            params = (limit,)
        
        detections = db_manager.execute_query(query, params)
        
        # Format the detections
        formatted_detections = []
        for detection in detections:
            # Check if this is the developer
            is_developer = detection[0] == os.environ.get('DEVELOPER_NAME', 'Roben Edwan')
            
            formatted_detections.append({
                'name': detection[0],
                'timestamp': detection[1],
                'confidence': detection[2],
                'emotion': detection[3],
                'greeting': detection[4],
                'recognized': True,
                'dev_mode': is_developer,
                'count': 1  # Single face
            })
        
        # Get profile counts
        profiles = face_detector.get_all_profiles() if face_detector else []
        profile_count = len(profiles) if profiles else 0
        
        return jsonify({
            'detections': formatted_detections,
            'profile_count': profile_count,
            'developer_mode': any(d['dev_mode'] for d in formatted_detections)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/recent-conversations', methods=['GET'])
def get_recent_conversations():
    """Get recent conversation history"""
    try:
        limit = request.args.get('limit', default=10, type=int)
        session_only = request.args.get('session_only', default=False, type=bool)
        
        if session_only:
            session_id = _get_or_create_session_id()
            query = """
                SELECT user_input, response, timestamp, emotion, intent, session_id
                FROM conversations
                WHERE session_id = %s
                ORDER BY timestamp DESC
                LIMIT %s
            """
            params = (session_id, limit)
        else:
            query = """
                SELECT user_input, response, timestamp, emotion, intent, session_id
                FROM conversations
                ORDER BY timestamp DESC
                LIMIT %s
            """
            params = (limit,)
        
        conversations = db_manager.execute_query(query, params)
        
        # Format the conversations
        formatted_conversations = []
        for conv in conversations:
            formatted_conversations.append({
                'user_input': conv[0],
                'response': conv[1],
                'timestamp': conv[2],
                'emotion': conv[3],
                'intent': conv[4],
                'session_id': conv[5] if len(conv) > 5 else None
            })
        
        return jsonify({
            'conversations': formatted_conversations,
            'count': len(formatted_conversations)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/voice-logs', methods=['GET'])
def get_voice_logs():
    """Get voice recognition logs"""
    try:
        limit = request.args.get('limit', default=20, type=int)
        session_only = request.args.get('session_only', default=False, type=bool)
        
        if session_only:
            session_id = _get_or_create_session_id()
            query = """
                SELECT text, timestamp, language, emotion, intent, session_id
                FROM voice_logs
                WHERE session_id = %s
                ORDER BY timestamp DESC
                LIMIT %s
            """
            params = (session_id, limit)
        else:
            query = """
                SELECT text, timestamp, language, emotion, intent, session_id
                FROM voice_logs
                ORDER BY timestamp DESC
                LIMIT %s
            """
            params = (limit,)
        
        logs = db_manager.execute_query(query, params)
        
        # Format the logs
        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                'text': log[0],
                'timestamp': log[1],
                'language': log[2],
                'emotion': log[3],
                'intent': log[4],
                'session_id': log[5] if len(log) > 5 else None
            })
        
        return jsonify({
            'logs': formatted_logs,
            'count': len(formatted_logs)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/profiles', methods=['GET'])
def get_profiles():
    """Get all saved profiles with metadata"""
    try:
        if not face_detector:
            return jsonify({'error': 'Face detection not available'}), 503
        
        profiles = face_detector.get_all_profiles()
        
        # For each profile, get the primary emotion
        for profile in profiles:
            try:
                if 'name' in profile:
                    profile['primary_emotion'] = emotion_tracker.get_primary_emotion_for_name(profile['name'])
            except:
                profile['primary_emotion'] = 'neutral'
        
        return jsonify({
            'profiles': profiles,
            'count': len(profiles),
            'success': True
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@api.route('/profile/<name>', methods=['GET'])
def get_profile(name):
    """Get a specific profile by name"""
    try:
        if not face_detector:
            return jsonify({'error': 'Face detection not available', 'success': False}), 503
        
        # Get all profiles and find the one with matching name
        profiles = face_detector.get_all_profiles()
        profile = next((p for p in profiles if p.get('name') == name), None)
        
        if not profile:
            return jsonify({'error': f'Profile not found for name: {name}', 'success': False}), 404
        
        # Add emotion data if available
        try:
            # Get the primary emotion from the emotion tracker
            profile['primary_emotion'] = emotion_tracker.get_primary_emotion_for_name(name)
        except:
            profile['primary_emotion'] = 'neutral'
        
        return jsonify({
            'profile': profile,
            'success': True
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@api.route('/log-recognition', methods=['POST'])
def log_face_recognition():
    """Log a face recognition event"""
    try:
        data = request.json
        name = data.get('name', 'Unknown')
        confidence = data.get('confidence', 0.0)
        emotion = data.get('emotion', 'neutral')
        greeting = data.get('greeting', None)
        
        session_id = _get_or_create_session_id()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log to recognition history
        db_manager.execute_query(
            """
            INSERT INTO recognition_history (name, timestamp, confidence, emotion, greeting, session_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (name, timestamp, confidence, emotion, greeting, session_id)
        )
        
        # Check if this is the developer
        is_developer = name == os.environ.get('DEVELOPER_NAME', 'Roben Edwan')
        
        return jsonify({
            'success': True,
            'timestamp': timestamp,
            'developer_mode': is_developer
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/log-emotion', methods=['POST'])
def log_emotion():
    """Log an emotion detection event"""
    try:
        data = request.json
        emotion = data.get('emotion', 'neutral')
        text = data.get('text', '')
        source = data.get('source', 'text')
        intensity = data.get('intensity', 0.5)
        
        # Log the emotion
        session_id = _get_or_create_session_id()
        emotion_tracker.log_emotion(emotion, text, source, intensity, session_id)
        
        return jsonify({
            'success': True,
            'emotion': emotion,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/retrain-emotion-model', methods=['POST'])
def retrain_emotion_model():
    """Trigger emotion model retraining"""
    try:
        # Check for developer mode
        developer_mode = False
        developer_name = os.environ.get('DEVELOPER_NAME', 'Roben Edwan')
        
        # Check if the developer's face was recently detected
        recent_recognitions = db_manager.execute_query(
            """
            SELECT name, timestamp FROM recognition_history 
            WHERE name = %s AND timestamp > NOW() - INTERVAL '30 minutes'
            ORDER BY timestamp DESC LIMIT 1
            """,
            (developer_name,)
        )
        
        if recent_recognitions and len(recent_recognitions) > 0:
            developer_mode = True
        
        # Only allow retraining in developer mode
        if not developer_mode and os.environ.get('REQUIRE_DEV_MODE_FOR_TRAINING', 'true').lower() == 'true':
            return jsonify({
                'success': False,
                'error': 'Developer mode required for model retraining'
            }), 403
        
        # Trigger retraining
        emotion_tracker.retrain_model()
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/sessions', methods=['GET'])
def get_sessions():
    """Get a list of available sessions"""
    try:
        # Query the sessions table
        sessions = db_manager.execute_query(
            """
            SELECT id, start_time, user_name, device_info 
            FROM sessions
            ORDER BY start_time DESC
            LIMIT 20
            """
        )
        
        # Format the sessions
        formatted_sessions = []
        for session in sessions:
            formatted_sessions.append({
                'id': session[0],
                'start_time': session[1],
                'user_name': session[2],
                'device_info': session[3]
            })
        
        return jsonify({
            'success': True,
            'sessions': formatted_sessions,
            'count': len(formatted_sessions)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/sms', methods=['POST'])
def send_sms():
    """Send SMS notification via Twilio with enhanced UAE number support"""
    try:
        # Support both JSON and form data for flexibility
        if request.is_json:
            data = request.json
        else:
            data = request.form.to_dict()
            
        # Support multiple parameter names for better API compatibility
        to_number = data.get('to_number') or data.get('phone_number') or data.get('to') or data.get('number')
        message = data.get('message') or data.get('text') or data.get('body') or data.get('content')
        
        # Special handling for owner shortcuts
        if to_number and to_number.lower() in ["roben", "owner", "admin", "me", "creator"]:
            import os
            owner_number = os.environ.get("OWNER_PHONE_NUMBER")
            if owner_number:
                logger.info(f"API: Using owner shortcut: Converting '{to_number}' to owner's number")
                to_number = owner_number
            else:
                logger.warning("API: Owner shortcut used but OWNER_PHONE_NUMBER not set")
                
        # Special handling for Roben's number in any format
        roben_patterns = ["522233989", "0522233989", "971522233989", "00971522233989", "+971522233989"]
        if to_number and any(pattern in to_number for pattern in roben_patterns):
            logger.info("API: Detected Roben's number, using standardized format")
            to_number = "+971522233989"
        
        if not to_number or not message:
            return jsonify({
                'success': False,
                'error': 'Both recipient number and message are required',
                'required_fields': {
                    'to_number': 'Recipient phone number in E.164 format (+971XXXXXXXXX)',
                    'message': 'Text message to send'
                },
                'help': {
                    'uae_format': 'For UAE numbers, use +971XXXXXXXXX or 05XXXXXXXX format',
                    'shortcuts': 'You can use "owner", "roben", "admin", or "me" to send to the owner'
                }
            }), 400
            
        # Initialize Twilio handler
        from twilio_handler import TwilioHandler
        twilio_handler = TwilioHandler()
        
        # Check if Twilio is available
        if not twilio_handler.is_available():
            import os
            missing_env_vars = []
            if not os.environ.get("TWILIO_ACCOUNT_SID"):
                missing_env_vars.append("TWILIO_ACCOUNT_SID")
            if not os.environ.get("TWILIO_AUTH_TOKEN"):
                missing_env_vars.append("TWILIO_AUTH_TOKEN")
            if not os.environ.get("TWILIO_PHONE_NUMBER"):
                missing_env_vars.append("TWILIO_PHONE_NUMBER")
                
            return jsonify({
                'success': False,
                'error': 'Twilio service is not available.',
                'missing_credentials': missing_env_vars,
                'solution': 'Please set the required Twilio environment variables and restart the server.'
            }), 503
        
        # Save original number for reference and logging
        original_number = to_number
        
        # Clean up phone number
        if to_number:
            # Remove spaces, dashes, brackets
            to_number = to_number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
            # UAE format handling - similar to main.py
            if not to_number.startswith('+'):
                if to_number.startswith('0097'):
                    # Convert 00971-style to +971
                    to_number = '+' + to_number[2:]
                elif to_number.startswith('97') and len(to_number) >= 10:
                    # Convert 971-style to +971
                    to_number = '+' + to_number
                elif to_number.startswith('05') and len(to_number) >= 9:
                    # Convert UAE local format (05x) to international (+971 5x)
                    to_number = '+971' + to_number[1:]
                elif to_number.startswith('5') and len(to_number) >= 8:
                    # Handle bare UAE mobile numbers (5xxxxxxxx)
                    to_number = '+971' + to_number
                elif to_number.startswith('00'):
                    # Handle double-zero prefixed international format (instead of +)
                    to_number = '+' + to_number[2:]
                else:
                    # Generic fallback - add + prefix
                    to_number = '+' + to_number
                    
                logger.info(f"API: Reformatted number from '{original_number}' to '{to_number}'")
            
        # Log the attempt with sanitized number for privacy
        sanitized_number = to_number[:6] + "XXXX" if len(to_number) > 6 else "XXXXXX"
        logger.info(f"API: Attempting to send SMS to {sanitized_number}")
            
        # Send the message
        result = twilio_handler.send_message(to_number, message)
        
        if result.get('success', False):
            # Log success but with sanitized number for privacy
            logger.info(f"API: Successfully sent SMS to {sanitized_number}")
            
            # Create a response with detailed information
            from datetime import datetime
            return jsonify({
                'success': True,
                'message': f'SMS sent successfully',
                'details': {
                    'sid': result.get('sid', ''),
                    'to': sanitized_number,
                    'from': result.get('from', ''),
                    'segments': result.get('segments', 1),
                    'length': result.get('length', len(message)),
                    'timestamp': datetime.now().isoformat(),
                    'message_preview': message[:20] + '...' if len(message) > 20 else message
                }
            })
        else:
            # Extract error details from the result
            error_message = result.get('error', 'Failed to send SMS')
            solution = result.get('solution', '')
            details = result.get('details', '')
            error_type = result.get('error_type', 'unknown_error')
            
            # Log the error
            logger.error(f"API: SMS sending failed: {error_message}")
            if details:
                logger.error(f"API: SMS error details: {details}")
            
            # Create error response
            response = {
                'success': False,
                'error': error_message,
                'error_type': error_type
            }
            
            # Add optional fields if available
            if solution:
                response['solution'] = solution
                logger.info(f"API: SMS error solution: {solution}")
            if details:
                response['details'] = details
            
            # Add UAE-specific help if available
            if 'uae_number_info' in result:
                response['uae_number_info'] = result['uae_number_info']
            elif '+971' in to_number or '971' in to_number or '05' in original_number:
                # Add UAE format helpers even if not provided by the handler
                response['uae_number_info'] = {
                    'examples': ['+971522233989', '+971501234567'],
                    'format_info': 'UAE mobile numbers start with "5" after the country code',
                    'local_format': 'Local format: 05XXXXXXXX',
                    'international_format': 'International format: +971XXXXXXXX' 
                }
                
            # Get appropriate status code
            status_code = 400 if error_type in ['invalid_number_format', 'trial_account_restriction'] else 500
                
            return jsonify(response), status_code
                
    except Exception as e:
        error_message = str(e)
        logger.error(f"API: Exception in send_sms endpoint: {error_message}")
        import traceback
        
        return jsonify({
            'success': False, 
            'error': 'Server error processing SMS request',
            'details': error_message,
            'traceback': traceback.format_exc()
        }), 500

@api.route('/ai-models', methods=['GET'])
def get_ai_models():
    """Get information about available AI models"""
    try:
        if not model_router:
            return jsonify({
                'success': False,
                'error': 'AI Model Router not available',
                'models': []
            }), 503
        
        # Get model status
        model_status = model_router.get_status()
        
        # Format response for API clients
        response = {
            'success': True,
            'model_backend': model_status.get('model_backend', ''),
            'available_models': model_status.get('available_models', {}),
            'ollama_running': model_status.get('ollama_running', False),
            'openai_configured': model_status.get('openai_configured', False),
            'request_count': model_status.get('request_count', 0),
            'error_count': model_status.get('error_count', 0),
            'last_model_used': model_status.get('last_model_used', None)
        }
        
        # Calculate status summary
        response['status'] = 'online' if (response['ollama_running'] or response['openai_configured']) else 'offline'
        
        # Calculate available and recommended models
        all_models = []
        if response['ollama_running'] and 'ollama' in response['available_models']:
            all_models.extend(response['available_models']['ollama'])
        if response['openai_configured'] and 'openai' in response['available_models']:
            all_models.extend(response['available_models']['openai'])
        
        response['models'] = all_models
        response['recommended_model'] = model_router.get_default_model()
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error getting AI models: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'models': []
        }), 500

@api.route('/ai-query', methods=['POST'])
def ai_query():
    """Send a direct query to the selected AI model"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Extract query parameters
        query = data.get('query')
        model_name = data.get('model')
        system_prompt = data.get('system_prompt')
        temperature = data.get('temperature', 0.7)
        
        # Validate query
        if not query or not isinstance(query, str) or len(query.strip()) == 0:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        # Log the request
        logger.info(f"AI query request: query='{query[:50]}...', model={model_name}, temperature={temperature}")
        
        if not model_router:
            return jsonify({
                'success': False,
                'error': 'AI Model Router not available'
            }), 503
        
        # Send to AI model
        start_time = time.time()
        response = model_router.generate_response(
            prompt=query,
            model=model_name,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=500,
            stream=False
        )
        end_time = time.time()
        
        # Calculate processing time
        processing_time = end_time - start_time
        
        # Format API response
        result = {
            'success': response.get('success', False),
            'content': response.get('content', None),
            'model': response.get('model', model_name),
            'processing_time': processing_time,
            'timestamp': response.get('timestamp', time.time())
        }
        
        # Add error if present
        if not result['success']:
            result['error'] = response.get('error', 'Unknown error')
            logger.warning(f"AI query failed: {result['error']}")
            return jsonify(result), 500
        
        # Log successful response
        logger.info(f"AI query successful: model={result['model']}, time={processing_time:.2f}s")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error processing AI query: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'content': None
        }), 500

@api.route('/sms-alert', methods=['POST'])
def send_sms_alert():
    """Send SMS notification with pre-formatted alert message with enhanced error handling"""
    try:
        # Support both JSON and form data for flexibility
        if request.is_json:
            data = request.json
        else:
            data = request.form.to_dict()
        
        # Support multiple parameter names for better API compatibility
        to_number = data.get('to_number') or data.get('phone_number') or data.get('to') or data.get('number')
        alert_type = data.get('alert_type') or data.get('type') or data.get('notification_type') or 'default'
        
        # Support either direct alert_data object or individual parameters
        alert_data = data.get('alert_data', {})
        
        # If no alert_data provided but individual parameters are, build alert_data dynamically
        if not alert_data and isinstance(data, dict):
            # Filter out known non-data parameters
            excluded_keys = ['to_number', 'phone_number', 'to', 'number', 'alert_type', 'type', 'notification_type', 'alert_data']
            # Add all remaining parameters to alert_data
            alert_data = {k: v for k, v in data.items() if k not in excluded_keys}
        
        # Special handling for owner shortcuts
        if to_number and to_number.lower() in ["roben", "owner", "admin", "me", "creator"]:
            import os
            owner_number = os.environ.get("OWNER_PHONE_NUMBER")
            if owner_number:
                logger.info(f"API: Using owner shortcut: Converting '{to_number}' to owner's number")
                to_number = owner_number
            else:
                logger.warning("API: Owner shortcut used but OWNER_PHONE_NUMBER not set")
                
        # Special handling for Roben's number in any format
        roben_patterns = ["522233989", "0522233989", "971522233989", "00971522233989", "+971522233989"]
        if to_number and any(pattern in to_number for pattern in roben_patterns):
            logger.info("API: Detected Roben's number, using standardized format")
            to_number = "+971522233989"
        
        if not to_number:
            return jsonify({
                'success': False,
                'error': 'Recipient phone number is required',
                'required_fields': {
                    'to_number': 'Recipient phone number in E.164 format (+971XXXXXXXXX)'
                },
                'help': {
                    'uae_format': 'For UAE numbers, use +971XXXXXXXXX or 05XXXXXXXX format',
                    'shortcuts': 'You can use "owner", "roben", "admin", or "me" to send to the owner'
                }
            }), 400
            
        # Initialize Twilio handler
        from twilio_handler import TwilioHandler
        twilio_handler = TwilioHandler()
        
        # Check if Twilio is available
        if not twilio_handler.is_available():
            import os
            missing_env_vars = []
            if not os.environ.get("TWILIO_ACCOUNT_SID"):
                missing_env_vars.append("TWILIO_ACCOUNT_SID")
            if not os.environ.get("TWILIO_AUTH_TOKEN"):
                missing_env_vars.append("TWILIO_AUTH_TOKEN")
            if not os.environ.get("TWILIO_PHONE_NUMBER"):
                missing_env_vars.append("TWILIO_PHONE_NUMBER")
                
            return jsonify({
                'success': False,
                'error': 'Twilio service is not available.',
                'missing_credentials': missing_env_vars,
                'solution': 'Please set the required Twilio environment variables and restart the server.'
            }), 503
            
        # Save original number for reference and logging
        original_number = to_number
        
        # Clean up phone number
        if to_number:
            # Remove spaces, dashes, brackets
            to_number = to_number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
            # UAE format handling - similar to main.py
            if not to_number.startswith('+'):
                if to_number.startswith('0097'):
                    # Convert 00971-style to +971
                    to_number = '+' + to_number[2:]
                elif to_number.startswith('97') and len(to_number) >= 10:
                    # Convert 971-style to +971
                    to_number = '+' + to_number
                elif to_number.startswith('05') and len(to_number) >= 9:
                    # Convert UAE local format (05x) to international (+971 5x)
                    to_number = '+971' + to_number[1:]
                elif to_number.startswith('5') and len(to_number) >= 8:
                    # Handle bare UAE mobile numbers (5xxxxxxxx)
                    to_number = '+971' + to_number
                elif to_number.startswith('00'):
                    # Handle double-zero prefixed international format (instead of +)
                    to_number = '+' + to_number[2:]
                else:
                    # Generic fallback - add + prefix
                    to_number = '+' + to_number
                    
                logger.info(f"API: Reformatted number from '{original_number}' to '{to_number}'")
        
        # Validate alert type
        valid_alert_types = [
            'alert', 'emotion', 'emotion_alert', 'face', 'face_new', 
            'face_familiar', 'security', 'system', 'error', 'status',
            'voice', 'command', 'greeting', 'response', 'learning',
            'reminder', 'update', 'info', 'uae_alert', 'default'
        ]
        
        if alert_type not in valid_alert_types:
            logger.warning(f"API: Unknown alert type '{alert_type}', defaulting to 'default'")
            # For backward compatibility, don't return an error, just use default
            alert_type = 'default'
            alert_data['message'] = alert_data.get('message', f"Alert from Robin AI ({alert_type})")
        
        # Get additional context for alerts if needed
        if alert_type == 'system' and not alert_data.get('message'):
            # Add system status info for system alerts
            import os
            hostname = os.environ.get('HOSTNAME', 'unknown')
            from datetime import datetime
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            alert_data['message'] = f"System status notification from Robin AI at {current_time}"
            
        # Add timestamp if not disabled
        if alert_data.get('include_timestamp', True) and 'timestamp' not in alert_data:
            from datetime import datetime
            alert_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        # Log the attempt with sanitized number for privacy
        sanitized_number = to_number[:6] + "XXXX" if len(to_number) > 6 else "XXXXXX"
        logger.info(f"API: Attempting to send SMS alert ({alert_type}) to {sanitized_number}")
            
        # Send the notification with the specified alert type
        result = twilio_handler.send_notification(to_number, alert_type, **alert_data)
        
        if result.get('success', False):
            # Log success but with sanitized number for privacy
            logger.info(f"API: Successfully sent SMS alert ({alert_type}) to {sanitized_number}")
            
            # Create a response with detailed information
            from datetime import datetime
            return jsonify({
                'success': True,
                'message': f'SMS alert sent successfully',
                'details': {
                    'sid': result.get('sid', ''),
                    'to': sanitized_number,
                    'from': result.get('from', ''),
                    'alert_type': alert_type,
                    'timestamp': datetime.now().isoformat(),
                    'segments': result.get('segments', 1),
                    'length': result.get('length', 0)
                }
            })
        else:
            # Extract error details from the result
            error_message = result.get('error', 'Failed to send SMS alert')
            solution = result.get('solution', '')
            details = result.get('details', '')
            error_type = result.get('error_type', 'unknown_error')
            
            # Log the error
            logger.error(f"API: SMS alert sending failed: {error_message}")
            if details:
                logger.error(f"API: SMS alert error details: {details}")
            
            # Create error response
            response = {
                'success': False,
                'error': error_message,
                'error_type': error_type,
                'alert_type': alert_type
            }
            
            # Add optional fields if available
            if solution:
                response['solution'] = solution
                logger.info(f"API: SMS alert error solution: {solution}")
            if details:
                response['details'] = details
            
            # Add UAE-specific help if available
            if 'uae_number_info' in result:
                response['uae_number_info'] = result['uae_number_info']
            elif '+971' in to_number or '971' in to_number or '05' in original_number:
                # Add UAE format helpers even if not provided by the handler
                response['uae_number_info'] = {
                    'examples': ['+971522233989', '+971501234567'],
                    'format_info': 'UAE mobile numbers start with "5" after the country code',
                    'local_format': 'Local format: 05XXXXXXXX',
                    'international_format': 'International format: +971XXXXXXXX' 
                }
                
            # Get appropriate status code
            status_code = 400 if error_type in ['invalid_number_format', 'trial_account_restriction'] else 500
                
            return jsonify(response), status_code
            
    except Exception as e:
        error_message = str(e)
        logger.error(f"API: Exception in send_sms_alert endpoint: {error_message}")
        import traceback
        
        return jsonify({
            'success': False, 
            'error': 'Server error processing SMS alert request',
            'details': error_message,
            'traceback': traceback.format_exc()
        }), 500

@api.route('/session-data', methods=['GET'])
def get_session_data():
    """Get comprehensive data for a specific session"""
    try:
        # Get session ID from query parameters or use current session
        session_id = request.args.get('session_id', None)
        if session_id == 'current' or not session_id:
            session_id = _get_or_create_session_id()
        
        # Get session info
        session_info = db_manager.execute_query(
            """
            SELECT id, start_time, user_name, device_info, metadata
            FROM sessions
            WHERE id = %s
            """,
            (session_id,)
        )
        
        if not session_info or len(session_info) == 0:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        # Get emotions for this session
        emotions_query = """
            SELECT emotion, COUNT(emotion) as count
            FROM emotion_data
            WHERE session_id = %s
            GROUP BY emotion
            ORDER BY count DESC
        """
        emotion_counts = db_manager.execute_query(emotions_query, (session_id,))
        
        emotions = {}
        for emotion in emotion_counts:
            emotions[emotion[0]] = emotion[1]
        
        # Get emotion timeline
        timeline_query = """
            SELECT emotion, timestamp, intensity, text, source
            FROM emotion_data
            WHERE session_id = %s
            ORDER BY timestamp ASC
        """
        timeline_data = db_manager.execute_query(timeline_query, (session_id,))
        
        emotion_timeline = []
        for data in timeline_data:
            emotion_timeline.append({
                'emotion': data[0],
                'timestamp': data[1],
                'intensity': data[2],
                'text': data[3],
                'source': data[4]
            })
        
        # Get interactions (conversations and voice logs)
        interactions_query = """
            SELECT 'text' as source, user_input as text, timestamp, emotion, intent
            FROM conversations
            WHERE session_id = %s
            UNION ALL
            SELECT 'voice' as source, text, timestamp, emotion, intent
            FROM voice_logs
            WHERE session_id = %s
            ORDER BY timestamp DESC
        """
        interactions_data = db_manager.execute_query(interactions_query, (session_id, session_id))
        
        interactions = []
        for data in interactions_data:
            interactions.append({
                'source': data[0],
                'text': data[1],
                'timestamp': data[2],
                'emotion': data[3],
                'intent': data[4]
            })
        
        # Get face recognitions
        face_query = """
            SELECT name, timestamp, confidence, emotion, greeting
            FROM recognition_history
            WHERE session_id = %s
            ORDER BY timestamp DESC
        """
        face_data = db_manager.execute_query(face_query, (session_id,))
        
        face_recognitions = []
        for data in face_data:
            face_recognitions.append({
                'name': data[0],
                'timestamp': data[1],
                'confidence': data[2],
                'emotion': data[3],
                'greeting': data[4]
            })
        
        # Calculate session statistics
        stats = {
            'total_interactions': len(interactions),
            'unique_emotions': len(emotions),
            'unique_users': len(set(fr['name'] for fr in face_recognitions)) if face_recognitions else 0,
            'duration': 'N/A'
        }
        
        # Calculate session duration
        if interactions:
            try:
                start_time = datetime.strptime(session_info[0][1], "%Y-%m-%d %H:%M:%S")
                latest_time = max([
                    datetime.strptime(i['timestamp'], "%Y-%m-%d %H:%M:%S") 
                    for i in interactions if i['timestamp']
                ])
                
                duration = latest_time - start_time
                minutes = int(duration.total_seconds() / 60)
                
                if minutes < 60:
                    stats['duration'] = f"{minutes} min"
                else:
                    hours = minutes // 60
                    mins = minutes % 60
                    stats['duration'] = f"{hours}h {mins}m"
            except:
                # If there's any error in calculation, use default
                stats['duration'] = 'N/A'
        
        return jsonify({
            'success': True,
            'session': {
                'id': session_info[0][0],
                'start_time': session_info[0][1],
                'user_name': session_info[0][2],
                'device_info': session_info[0][3],
                'metadata': json.loads(session_info[0][4]) if session_info[0][4] else {}
            },
            'emotions': emotions,
            'emotion_timeline': emotion_timeline,
            'interactions': interactions,
            'face_recognitions': face_recognitions,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500