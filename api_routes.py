import os
import json
import time
import uuid
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, session

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

def init_api(app, _db_manager, _emotion_tracker, _face_detector, 
            _tts_manager, _voice_recognition, _intent_classifier, _config):
    """Initialize the API blueprint with necessary dependencies"""
    global db_manager, emotion_tracker, face_detector, tts_manager, voice_recognition, intent_classifier, config
    
    # Store references to core components
    db_manager = _db_manager
    emotion_tracker = _emotion_tracker
    face_detector = _face_detector
    tts_manager = _tts_manager
    voice_recognition = _voice_recognition
    intent_classifier = _intent_classifier
    config = _config
    
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
                    
            print(f"🔍 API Request: {api_info}")

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
            print(f"Error checking developer mode: {e}")
        
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
        
        # Emotion data
        if session_only and session_id:
            # Get emotions from specific session
            emotion_data = emotion_tracker.get_session_emotion_history(session_id)
        elif session_only:
            # Get emotions from current session
            session_id = _get_or_create_session_id()
            emotion_data = emotion_tracker.get_session_emotion_history(session_id)
        else:
            # Get all emotions within timeframe
            emotion_data = emotion_tracker.get_emotion_history(days)
        
        # Calculate overall distribution
        total_entries = emotion_tracker.get_total_entries()
        
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
    """Send SMS notification via Twilio"""
    try:
        data = request.json
        to_number = data.get('to_number')
        message = data.get('message')
        
        if not to_number or not message:
            return jsonify({
                'success': False,
                'error': 'Both to_number and message are required'
            }), 400
            
        # Initialize Twilio handler
        from twilio_handler import TwilioHandler
        twilio_handler = TwilioHandler()
        
        # Check if Twilio is available
        if not twilio_handler.is_available():
            return jsonify({
                'success': False,
                'error': 'Twilio service not available. Check credentials.'
            }), 503
            
        # Send the message
        try:
            result = twilio_handler.send_message(to_number, message)
            
            if result["success"]:
                return jsonify({
                    'success': True,
                    'message': 'SMS sent successfully',
                    'to': result.get('to', to_number),
                    'sid': result.get('sid', '')
                })
            else:
                # Get status code based on error type
                status_code = 500
                if "Invalid 'To' Phone Number" in result.get('details', ''):
                    status_code = 400
                    result['error'] = f'Invalid phone number format: {to_number}. Use E.164 format (+[country code][number]).'
                
                return jsonify(result), status_code
        except Exception as e:
            error_msg = str(e)
            return jsonify({
                'success': False,
                'error': 'Unexpected error in SMS handling',
                'details': error_msg
            }), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/sms-alert', methods=['POST'])
def send_sms_alert():
    """Send SMS notification with pre-formatted alert message"""
    try:
        data = request.json
        to_number = data.get('to_number')
        alert_type = data.get('alert_type', 'default')
        alert_data = data.get('alert_data', {})
        
        if not to_number:
            return jsonify({
                'success': False,
                'error': 'to_number is required'
            }), 400
            
        # Initialize Twilio handler
        from twilio_handler import TwilioHandler
        twilio_handler = TwilioHandler()
        
        # Check if Twilio is available
        if not twilio_handler.is_available():
            return jsonify({
                'success': False,
                'error': 'Twilio service not available. Check credentials.'
            }), 503
            
        # Send the notification with the specified alert type
        try:
            result = twilio_handler.send_notification(to_number, alert_type, **alert_data)
            
            if result["success"]:
                return jsonify({
                    'success': True,
                    'message': 'SMS alert sent successfully',
                    'to': result.get('to', to_number),
                    'sid': result.get('sid', ''),
                    'alert_type': result.get('alert_type', alert_type)
                })
            else:
                # Get status code based on error type
                status_code = 500
                if "Invalid 'To' Phone Number" in result.get('details', ''):
                    status_code = 400
                    result['error'] = f'Invalid phone number format: {to_number}. Use E.164 format (+[country code][number]).'
                
                return jsonify(result), status_code
        except Exception as e:
            error_msg = str(e)
            return jsonify({
                'success': False,
                'error': 'Unexpected error in SMS alert handling',
                'details': error_msg
            }), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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