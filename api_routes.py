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
    
    # Register the blueprint
    app.register_blueprint(api, url_prefix='/api')

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
        
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/emotion-data', methods=['GET'])
def get_emotion_data():
    """Get emotion data for visualization"""
    try:
        # Time period (days)
        days = request.args.get('days', default=7, type=int)
        session_only = request.args.get('session_only', default=False, type=bool)
        
        # Emotion data
        if session_only:
            # Only get emotions from current session
            session_id = _get_or_create_session_id()
            emotion_data = emotion_tracker.get_session_emotion_history(session_id)
        else:
            # Get all emotions within timeframe
            emotion_data = emotion_tracker.get_emotion_history(days)
        
        # Calculate overall distribution
        total_entries = emotion_tracker.get_total_entries()
        
        # Return formatted data
        return jsonify({
            'timeline': emotion_data,
            'total_entries': total_entries,
            'days': days,
            'session_only': session_only
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
            'count': len(profiles)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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