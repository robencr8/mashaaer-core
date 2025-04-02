import os
import logging
import json
import traceback
import socket
from urllib.parse import urlparse
from flask import Flask, render_template, request, jsonify, Response, redirect, url_for, session, abort
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import threading
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import core components
from config import Config
from core_launcher import CoreLauncher
from emotion_tracker import EmotionTracker
from intent_classifier import IntentClassifier
from database.db_manager import DatabaseManager
from tts.tts_manager import TTSManager
from auto_learning import AutoLearning
from voice.recognition import VoiceRecognition
from vision.face_detector import FaceDetector
from twilio_handler import TwilioHandler

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "robin_ai_default_secret")
# Enable CORS for all routes to support Flutter and mobile app integration
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Cache-busting function to prevent stale assets
BUILD_VERSION = str(int(time.time()))  # Use timestamp as version
def versioned_url(filename):
    """Add version parameter to static asset URLs for cache-busting"""
    from flask import url_for
    return url_for('static', filename=filename, v=BUILD_VERSION)

# Initialize components
config = Config()
db_manager = DatabaseManager(config=config, db_path=config.DB_PATH)
emotion_tracker = EmotionTracker(db_manager)
tts_manager = TTSManager(config)
intent_classifier = IntentClassifier()
voice_recognition = VoiceRecognition(config)
face_detector = FaceDetector(config, db_manager)
auto_learning = AutoLearning(db_manager)
twilio_handler = TwilioHandler()
from profile_manager import ProfileManager
profile_manager = ProfileManager(db_manager)

# Initialize context assistant and AI model router
from context_assistant import ContextAssistant
from ai_model_router import AIModelRouter
context_assistant = ContextAssistant(db_manager, profile_manager, emotion_tracker, intent_classifier)
model_router = AIModelRouter()

# Initialize API routes
from api_routes import init_api
from api_routes_dev import init_developer_api
init_api(app, db_manager, emotion_tracker, face_detector, 
         tts_manager, voice_recognition, intent_classifier, config,
         context_assistant, model_router)

# Initialize Developer API routes
app.config['db_manager'] = db_manager
init_developer_api(app)

# Add /ask endpoint for direct AI interactions
@app.route('/ask', methods=['POST'])
def ask():
    """
    Endpoint for direct AI interaction with dynamic model switching
    
    Request format:
    {
        "input": "User query text",
        "model": "Optional model name"  # Defaults to MODEL_BACKEND env setting
    }
    
    Response format:
    {
        "response": "AI response text",
        "model": "Model used",
        "status": "success/error"
    }
    """
    import uuid  # Import uuid here
    
    try:
        # Log the request
        logger.info(f"Ask endpoint accessed from {request.remote_addr}")
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        # Extract user input
        user_input = data.get('input')
        model_name = data.get('model')
        system_prompt = data.get('system_prompt')
        
        # Validate input
        if not user_input or not isinstance(user_input, str) or len(user_input.strip()) == 0:
            return jsonify({
                'status': 'error',
                'message': 'Input is required'
            }), 400
        
        # Log the request
        logger.info(f"Ask request: input='{user_input[:50]}...'")
        
        # Store in session history
        session_id = session.get('session_id', str(uuid.uuid4()))
        session['session_id'] = session_id
        
        # Add to conversation history if database connection is available
        try:
            if db_manager:
                db_manager.execute_query(
                    "INSERT INTO conversation_history (session_id, user_input, timestamp) VALUES (%s, %s, %s)",
                    (session_id, user_input, time.time())
                )
        except Exception as db_error:
            logger.warning(f"Could not log conversation to database: {str(db_error)}")
        
        # Generate AI response using the model router
        response_data = model_router.generate_response(
            prompt=user_input,
            model=model_name,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=500
        )
        
        # Format the response
        if response_data.get('success', False):
            ai_response = response_data.get('content', '')
            model_used = response_data.get('model', 'unknown')
            
            # Store the response in history if database is available
            try:
                if db_manager and ai_response:
                    # PostgreSQL doesn't support ORDER BY/LIMIT in UPDATE statements the same way as SQLite
                    # First find the most recent matching conversation
                    find_query = """
                        SELECT id FROM conversation_history 
                        WHERE session_id = %s AND user_input = %s 
                        ORDER BY timestamp DESC LIMIT 1
                    """
                    result = db_manager.execute_query(find_query, (session_id, user_input))
                    
                    if result and len(result) > 0:
                        # Then update that specific record by ID
                        row_id = result[0][0]
                        db_manager.execute_query(
                            "UPDATE conversation_history SET ai_response = %s, model_used = %s WHERE id = %s",
                            (ai_response, model_used, row_id)
                        )
            except Exception as db_error:
                logger.warning(f"Could not update conversation history: {str(db_error)}")
            
            # Return the successful response
            return jsonify({
                'response': ai_response,
                'model': model_used,
                'status': 'success'
            })
        else:
            # Return the error
            error_message = response_data.get('error', 'Unknown error')
            error_type = response_data.get('error_type', 'unknown_error')
            fallback_reason = response_data.get('fallback_reason', None)
            
            # Log the error 
            logger.warning(f"AI response generation failed: {error_message}")
            
            response_json = {
                'status': 'error',
                'message': error_message,
                'model': response_data.get('model', 'unknown'),
                'error_type': error_type
            }
            
            # Add quota information if it's a quota issue
            if isinstance(error_message, str) and "quota" in error_message.lower():
                logger.error("OpenAI quota exceeded error detected in /ask endpoint")
                response_json['quota_exceeded'] = True
                
                # Check if this is the special "no-fallback" scenario
                if error_type == "quota_exceeded_no_fallback":
                    response_json['model_suggestion'] = "Install Ollama for local AI support when OpenAI is unavailable"
                    response_json['installation_suggestion'] = "Visit https://ollama.ai to download and install Ollama"
                else:
                    response_json['model_suggestion'] = "Use model='auto' to automatically fall back to Ollama models when OpenAI is unavailable"
            
            # Check for Ollama availability
            if 'ollama_available' in response_data:
                response_json['ollama_available'] = response_data['ollama_available']
                
            # Add fallback reason if available
            if fallback_reason:
                response_json['fallback_reason'] = fallback_reason
                
            return jsonify(response_json), 500
    
    except Exception as e:
        # Log the error
        logger.error(f"Error processing /ask request: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Add versioned_url helper to Jinja templates
app.jinja_env.globals.update(versioned_url=versioned_url)

# Developer mode constants
DEVELOPER_NAME = os.environ.get("DEVELOPER_NAME", "Roben Edwan")
DEVELOPER_MODE_FLAG = "dev_mode_enabled"

# Helper function to get developer mode status
def is_developer_mode():
    # Check session first (for current request)
    from flask import session
    if session.get(DEVELOPER_MODE_FLAG, False):
        return True

    # Then check database (persistent across sessions)
    try:
        value = db_manager.get_setting(DEVELOPER_MODE_FLAG, "false")
        if isinstance(value, str):
            return value.lower() == "true"
        return bool(value)
    except:
        return False

# Helper function to set developer mode
def set_developer_mode(enabled=True):
    # Update session
    from flask import session
    session[DEVELOPER_MODE_FLAG] = enabled

    # Update database
    db_manager.set_setting(DEVELOPER_MODE_FLAG, "true" if enabled else "false")

    logger.info(f"Developer mode {'enabled' if enabled else 'disabled'}")

from flask import request

# Function to check if request is coming from a local network
def is_local_network(host):
    """Check if host is on a local network"""
    if not host:
        return False
    return (
        host == 'localhost' or
        host == '127.0.0.1' or
        host.startswith('192.168.') or
        host.startswith('10.') or
        host.startswith('172.16.') or
        host.startswith('0.0.0.0') or
        '.local' in host
    )

# Function to get the public replit domain
def get_replit_domain():
    """Get the public Replit domain from environment variables"""
    replit_domain = os.environ.get("REPLIT_DOMAINS", "")
    # If there are multiple domains, use the first one
    if ',' in replit_domain:
        replit_domain = replit_domain.split(',')[0].strip()
    return replit_domain

@app.before_request
def handle_request_routing():
    """Handle request routing, redirecting, and logging"""
    # Get host and request details
    host = request.host.split(':')[0]  # Remove port if present
    full_url = request.url
    path = request.path
    
    # Check if we need to redirect to a proper domain
    replit_domain = get_replit_domain()
    
    # Get real URL scheme (HTTP/HTTPS) - Replit typically uses HTTPS
    scheme = 'https' if request.headers.get('X-Forwarded-Proto') == 'https' else request.scheme
    
    # Debug log for routing
    logger.debug(f"📍 Request: {full_url}, host: {host}, path: {path}, replit_domain: {replit_domain}")
    
    # Check if this is a Replit testing/feedback tool
    is_replit_tool = request.headers.get('User-Agent', '').lower().startswith('replit') or 'replit' in request.headers.get('User-Agent', '').lower()
    
    # For testing purposes, treat all localhost requests as coming from a Replit tool
    # This allows the web_application_feedback_tool to work properly
    if 'localhost' in host:
        is_replit_tool = True
        
    # Special handling for API requests, the '/ask' endpoint, or Replit tools: no redirects, just log
    if path.startswith('/api/') or path == '/ask' or is_replit_tool:
        # Log API requests with more detail
        api_info = {
            'endpoint': path,
            'method': request.method,
            'args': {k: v for k, v in request.args.items()},
            'content_type': request.content_type,
            'has_json': request.is_json,
            'host': host
        }
        # Add JSON data if available
        if request.is_json:
            try:
                api_info['json'] = request.get_json()
            except:
                api_info['json'] = 'Error parsing JSON'
                
        logger.info(f"🔍 API Request: {api_info}")
        return None  # Continue processing the request
    
    # Simple logging for regular routes
    logger.info(f"🔍 Request to: {path} from {host}")
    
    # For non-API routes, handle localhost redirection if needed
    # But only when not already running in the Replit environment
    # This prevents redirect loops and allows the feedback tool to work
    is_replit_env = 'replit.dev' in host or 'replit.com' in host
    in_dev_environment = os.environ.get('FLASK_ENV') == 'development'
    
    # If running in local network but not in Replit environment, redirect to domain
    # We already check for Replit tools above, no need to check again
    # Additional check for User-Agent will prevent redirection for Replit feedback tool
    
    if (is_local_network(host) and 
        replit_domain and 
        not is_replit_env and 
        not in_dev_environment and
        not 'localhost_testing' in request.args and
        not is_replit_tool):
        
        # Create redirect URL to the proper replit domain
        redirect_url = f"https://{replit_domain}{path}"
        if request.query_string:
            redirect_url += f"?{request.query_string.decode('utf-8')}"
            
        logger.info(f"🔀 Redirecting from local {host} to {replit_domain}")
        return redirect(redirect_url, code=302)
    
    # Check for legacy routes that need to be redirected to mobile interface
    return handle_legacy_route_redirects(path)

def handle_legacy_route_redirects(path):
    """Redirect legacy routes to the new mobile interface"""
    # Map of legacy routes to mobile replacements
    legacy_routes = {
        '/index.html': 'mobile_splash',
        '/dashboard': 'mobile_index',
        '/emotions': 'mobile_emotions',
        '/profile.html': 'mobile_profiles',
        '/settings': 'mobile_settings',
        '/help': 'mobile_help',
        '/contact': 'mobile_contact',
        '/admin.html': 'mobile_settings',
        '/sms.html': 'mobile_settings',
        '/session-data': 'mobile_emotions'
    }
    
    # Check if this is a legacy route that needs redirection
    for legacy_path, mobile_route in legacy_routes.items():
        if path == legacy_path:
            logger.info(f"📱 Redirecting legacy route {path} to {mobile_route}")
            return redirect(url_for(mobile_route), code=302)
    
    # Not a legacy route, continue with normal request processing
    return None

# Scheduler for auto-learning
scheduler = BackgroundScheduler()

# Initialize core launcher
core_launcher = CoreLauncher(
    config=config,
    db_manager=db_manager,
    emotion_tracker=emotion_tracker,
    tts_manager=tts_manager,
    intent_classifier=intent_classifier,
    voice_recognition=voice_recognition,
    face_detector=face_detector
)

# Routes
@app.route('/')
def index():
    # Always redirect to the cosmic mobile UI
    return redirect(url_for('mobile_splash'))
    
    # Legacy code, no longer used
    # Check if onboarding has been completed
    # onboarding_status = db_manager.get_setting('onboarding_complete', 'false')
    # onboarding_complete = False
    # 
    # if isinstance(onboarding_status, str):
    #     onboarding_complete = onboarding_status.lower() == 'true'
    # 
    # # If onboarding not complete, redirect to startup
    # if not onboarding_complete:
    #     return redirect(url_for('startup'))
    # 
    # dev_mode = is_developer_mode()
    # return render_template('index.html', dev_mode=dev_mode)

@app.route('/startup')
def startup():
    # Always redirect to the cosmic mobile UI
    welcome_message = "Welcome to Robin AI. Let's get started with your onboarding."
    tts_manager.speak(welcome_message, 'default', 'en', profile_manager)
    # Use mobile splash instead of old startup template
    return redirect(url_for('mobile_splash'))

@app.route('/consent')
def consent():
    # Always redirect to the cosmic mobile UI
    return redirect(url_for('mobile_index'))

@app.route('/voice-register')
def voice_register():
    # Always redirect to the cosmic mobile UI
    return redirect(url_for('mobile_index'))

@app.route('/goodbye')
def goodbye():
    # Always redirect to the cosmic mobile UI
    return redirect(url_for('mobile_index'))

@app.route('/demo')
def demo():
    # Redirect to mobile index which has the demo capabilities
    return redirect(url_for('mobile_index'))

@app.route('/emotion-timeline')
def emotion_timeline():
    # Redirect to mobile emotions page which has cosmic emotion visualization
    return redirect(url_for('mobile_emotions'))

@app.route('/profile')
def profile():
    # Redirect to mobile profiles page which has cosmic profile UI
    return redirect(url_for('mobile_profiles'))

@app.route('/live-view')
def live_view():
    # Redirect to mobile index which has the camera and voice capabilities built-in
    return redirect(url_for('mobile_index'))

@app.route('/enable-dev-mode')
def enable_dev_mode():
    """Enable developer mode for testing"""
    set_developer_mode(True)
    from flask import flash
    flash("Developer mode enabled", "success")
    return redirect(url_for('admin'))

@app.route('/admin')
def admin():
    # Only accessible in developer mode
    if not is_developer_mode():
        return redirect(url_for('mobile_index'))

    # For now, redirect to mobile settings which has the admin controls
    # Future: Create a dedicated mobile/admin.html template with cosmic UI
    return redirect(url_for('mobile_settings'))

@app.route('/sms-notifications')
def sms_notifications():
    # Only accessible in developer mode
    if not is_developer_mode():
        return redirect(url_for('mobile_index'))
    
    # For now, redirect to the mobile settings page which has a section for SMS
    # Future: Create a dedicated mobile/sms.html template with cosmic UI
    return redirect(url_for('mobile_settings'))

@app.route('/session-report')
def session_report():
    """Show the session report dashboard with real-time data visualization"""
    # Redirect to mobile emotions page which has cosmic emotion visualization
    return redirect(url_for('mobile_emotions'))

@app.route('/download/session.csv')
def download_session_csv():
    """Download session data as CSV"""
    from flask import session as flask_session
    import csv
    from io import StringIO
    
    # If not in developer mode, redirect to mobile UI
    if not is_developer_mode():
        return redirect(url_for('mobile_emotions'))

    # Get session ID from query parameters or use current session
    session_id = request.args.get('session_id', None)
    if session_id == 'current' or not session_id:
        session_id = flask_session.get('session_id')
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
            flask_session['session_id'] = session_id

    # Get emotion data for this session
    emotions_query = """
        SELECT emotion, timestamp, intensity, text, source
        FROM emotion_data
        WHERE session_id = %s
        ORDER BY timestamp ASC
    """
    emotion_data = db_manager.execute_query(emotions_query, (session_id,))

    # Create CSV in memory
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Emotion', 'Timestamp', 'Intensity', 'Text', 'Source'])

    for row in emotion_data:
        writer.writerow(row)

    output = si.getvalue()
    si.close()

    # Return the CSV as a file download
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=session_report.csv"}
    )

@app.route('/api/speak', methods=['POST'])
def speak():
    text = request.json.get('text', '')
    voice = request.json.get('voice', 'default')
    language = request.json.get('language', 'en-US')
    use_profile = request.json.get('use_profile', True)

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Use profile manager to get personalized voice and adapted text
        if use_profile:
            # Adapt text based on preferred tone
            adapted_text = profile_manager.adapt_response(text, language)

            # Get preferred voice for language if not explicitly specified
            if voice == 'default':
                voice = profile_manager.get_tts_voice_for_language(language)

            # Speak using profile-based settings
            audio_path = tts_manager.speak(adapted_text, voice, language, profile_manager)
        else:
            # Select basic voice based on language if not specifically provided
            if voice == 'default' and language == 'ar':
                voice = 'arabic'

            # Use standard TTS without profile-based customization
            audio_path = tts_manager.speak(text, voice)

        return jsonify({
            'success': True, 
            'audio_path': audio_path,
            'text': text,
            'voice': voice,
            'language': language
        })
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/listen', methods=['POST'])
def listen():
    audio_data = request.files.get('audio')

    if not audio_data:
        return jsonify({'error': 'No audio data provided'}), 400

    try:
        # Save temporary audio file
        temp_path = os.path.join(os.getcwd(), 'temp_audio.wav')
        audio_data.save(temp_path)

        # Process with voice recognition
        text = voice_recognition.process_audio(temp_path)

        # Check for developer mode trigger
        dev_mode = is_developer_mode()
        if DEVELOPER_NAME in text:
            dev_mode = set_developer_mode(True)
            logger.info("Developer mode activated via voice")

            # Special greeting for Roben
            if "name" in text.lower() and (DEVELOPER_NAME.lower() in text.lower()):
                greeting = "Welcome back, Roben. Robin AI is fully operational."
                tts_manager.speak(greeting, profile_manager=profile_manager)
                logger.info("Special greeting played for creator")

        # Process emotion
        emotion = emotion_tracker.analyze_text(text)

        # Get session ID for logging
        from flask import session
        session_id = session.get('session_id', None)
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id

        # Log emotion with session ID
        emotion_tracker.log_emotion(emotion, text, session_id=session_id)

        # Get intent
        intent = intent_classifier.classify(text)

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return jsonify({
            'success': True, 
            'text': text, 
            'emotion': emotion,
            'intent': intent,
            'dev_mode': dev_mode
        })

    except Exception as e:
        logger.error(f"Voice recognition error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/detect-face', methods=['POST'])
def detect_face():
    face_image = request.files.get('image')

    if not face_image:
        return jsonify({'error': 'No image provided'}), 400

    try:
        # Save temporary image file
        temp_path = os.path.join(os.getcwd(), 'temp_face.jpg')
        face_image.save(temp_path)

        # Process with face detector
        result = face_detector.detect_faces(temp_path)

        # Update last seen for recognized faces
        if result and result.get('count', 0) > 0:
            for face in result.get('faces', []):
                if face.get('recognized', False):
                    # Update the last seen timestamp for this face
                    face_detector._update_last_seen(face.get('name'))

                    # Attach an emotion if available based on metadata
                    face['emotion'] = emotion_tracker.get_primary_emotion_for_name(face.get('name', ''))

        # Check for developer mode trigger
        dev_mode = is_developer_mode()
        if result.get('faces') and any(face.get('name') == DEVELOPER_NAME for face in result.get('faces', [])):
            dev_mode = set_developer_mode(True)
            logger.info("Developer mode activated via face recognition")

            # Special greeting for Roben when detected by face
            greeting = "Welcome back, Roben. Robin AI is fully operational."
            tts_manager.speak(greeting, profile_manager=profile_manager)
            logger.info("Special greeting played for creator face detection")

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return jsonify({
            'success': True,
            'result': result,
            'dev_mode': dev_mode
        })

    except Exception as e:
        logger.error(f"Face detection error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/emotion-data')
def emotion_data():
    days = request.args.get('days', 7, type=int)
    session_id = request.args.get('session_id', None)
    mobile_format = request.args.get('mobile_format', 'false').lower() == 'true'
    
    if session_id:
        # Get emotions for a specific session
        emotions = emotion_tracker.get_session_emotion_history(session_id)
    else:
        # Get general emotion history
        emotions = emotion_tracker.get_emotion_history(days=days)
    
    # Convert timestamps to mobile-friendly format if requested
    if mobile_format and emotions and 'data' in emotions:
        for entry in emotions['data']:
            if 'timestamp' in entry:
                # Convert timestamp to Unix timestamp (milliseconds) for mobile
                try:
                    if isinstance(entry['timestamp'], str):
                        from datetime import datetime
                        dt = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                        entry['timestamp'] = int(dt.timestamp() * 1000)
                except Exception as e:
                    logger.error(f"Error converting timestamp: {str(e)}")
    
    return jsonify({
        'success': True,
        'emotions': emotions,
        'session_id': session_id,
        'days': days,
        'mobile_format': mobile_format
    })

@app.route('/api/add-face-profile', methods=['POST'])
def add_face_profile():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image provided'}), 400

    name = request.form.get('name')
    if not name:
        return jsonify({'success': False, 'error': 'No name provided'}), 400

    # Get metadata if available
    metadata = {}
    metadata_json = request.form.get('metadata')
    if metadata_json:
        try:
            metadata = json.loads(metadata_json)
        except:
            pass

    # Save image to temporary file
    image = request.files['image']
    temp_path = os.path.join(os.getcwd(), 'temp_profile.jpg')
    image.save(temp_path)

    try:
        # Add face to profiles
        result = face_detector.add_face(name, temp_path, metadata)

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        if result:
            logger.info(f"Added new face profile for {name}")
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to add face profile'}), 500

    except Exception as e:
        logger.error(f"Error adding face profile: {str(e)}")
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete-face-profile/<profile_id>', methods=['DELETE'])
def delete_face_profile(profile_id):
    try:
        # This would be implemented in the face_detector
        # For now, we'll return a mock response
        logger.info(f"Deleting face profile {profile_id}")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting face profile: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Profile API route moved to api_routes.py
def set_language():
    """Set the user's language preference"""
    try:
        data = request.json
        language = data.get('language')

        if not language:
            return jsonify({'success': False, 'error': 'Language preference is required'}), 400

        # Store in database
        db_manager.set_setting('language_preference', language)

        # Store in session
        from flask import session
        session['language'] = language

        # Update the user profile with the new language preference
        profile_data = {
            'language': language
        }
        profile_manager.update_profile(profile_data)

        # Get the appropriate voice for this language
        tts_voice = profile_manager.get_tts_voice_for_language(language)

        # Set voice and TTS preferences accordingly
        if language == 'ar':
            # Set Arabic voice if available
            tts_manager.speak("تم تحديد اللغة العربية", tts_voice, language, profile_manager)
        else:
            # Default to English voice
            tts_manager.speak("English language selected", tts_voice, language, profile_manager)

        return jsonify({
            'success': True,
            'message': 'Language preference set successfully'
        })

    except Exception as e:
        logger.error(f"Error setting language: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/send-sms', methods=['POST'])
def send_sms():
    """Send SMS notification with enhanced error handling and UAE number support"""
    if not is_developer_mode():
        return jsonify({
            'success': False, 
            'error': 'Not authorized',
            'solution': 'Enable developer mode to use SMS features'
        }), 403
        
    try:
        # Accept both JSON and form data for flexibility
        if request.is_json:
            data = request.json
        else:
            data = request.form.to_dict()
            
        # Get phone number from parameters, with multiple possible keys for flexibility
        phone_number = data.get('phone_number') or data.get('to') or data.get('number') or data.get('recipient')
        
        # Get message text with multiple possible keys
        message = data.get('message') or data.get('text') or data.get('content') or data.get('body')
        
        # Special handling for owner shortcuts
        if phone_number and phone_number.lower() in ["roben", "owner", "admin", "me", "creator"]:
            owner_number = os.environ.get("OWNER_PHONE_NUMBER")
            if owner_number:
                logger.info(f"Using owner shortcut: Converting '{phone_number}' to owner's number")
                phone_number = owner_number
            else:
                logger.warning("Owner shortcut used but OWNER_PHONE_NUMBER not set")
        
        # Special handling for Roben's number in any format
        roben_patterns = ["522233989", "0522233989", "971522233989", "00971522233989", "+971522233989"]
        if phone_number and any(pattern in phone_number for pattern in roben_patterns):
            logger.info("Detected Roben's number, using standardized format")
            phone_number = "+971522233989"
        
        if not phone_number or not message:
            return jsonify({
                'success': False, 
                'error': 'Phone number and message are required',
                'required_fields': {
                    'phone_number': 'Recipient phone number in E.164 format (+971XXXXXXXXX)',
                    'message': 'Text message to send'
                },
                'help': {
                    'uae_format': 'For UAE numbers, use +971XXXXXXXXX or 05XXXXXXXX format',
                    'shortcuts': 'You can use "owner", "roben", "admin", or "me" to send to the owner'
                }
            }), 400
            
        # Initialize Twilio handler
        twilio_handler = TwilioHandler()
        
        # Check if Twilio is available
        if not twilio_handler.is_available():
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
        
        # Clean up phone number
        original_number = phone_number  # Save for reference
        if phone_number:
            # Remove spaces, dashes, brackets
            phone_number = phone_number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
            # UAE format handling - more comprehensive than the twilio_handler
            if not phone_number.startswith('+'):
                if phone_number.startswith('0097'):
                    # Convert 00971-style to +971
                    phone_number = '+' + phone_number[2:]
                elif phone_number.startswith('97') and len(phone_number) >= 10:
                    # Convert 971-style to +971
                    phone_number = '+' + phone_number
                elif phone_number.startswith('05') and len(phone_number) >= 9:
                    # Convert UAE local format (05x) to international (+971 5x)
                    phone_number = '+971' + phone_number[1:]
                elif phone_number.startswith('5') and len(phone_number) >= 8:
                    # Handle bare UAE mobile numbers (5xxxxxxxx)
                    phone_number = '+971' + phone_number
                elif phone_number.startswith('00'):
                    # Handle double-zero prefixed international format (instead of +)
                    phone_number = '+' + phone_number[2:]
                else:
                    # Generic fallback - add + prefix
                    phone_number = '+' + phone_number
                    
                logger.info(f"Reformatted number from '{original_number}' to '{phone_number}'")
        
        # Log the attempt with sanitized number (show only first 6 digits)
        sanitized_number = phone_number[:6] + "XXXX" if len(phone_number) > 6 else "XXXXXX"
        logger.info(f"Attempting to send SMS to {sanitized_number}...")
            
        # Send the message
        result = twilio_handler.send_message(phone_number, message)
        
        if result.get('success', False):
            # Log success but with sanitized number for privacy
            logger.info(f"Successfully sent SMS to {sanitized_number}")
            
            # Create a response with detailed information
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
            logger.error(f"SMS sending failed: {error_message}")
            if details:
                logger.error(f"SMS error details: {details}")
            
            # Create error response
            response = {
                'success': False,
                'error': error_message,
                'error_type': error_type
            }
            
            # Add optional fields if available
            if solution:
                response['solution'] = solution
                logger.info(f"SMS error solution: {solution}")
            if details:
                response['details'] = details
            
            # Add UAE-specific help if available
            if 'uae_number_info' in result:
                response['uae_number_info'] = result['uae_number_info']
            elif '+971' in phone_number or '971' in phone_number or '05' in original_number:
                # Add UAE format helpers even if not provided by the handler
                response['uae_number_info'] = {
                    'examples': ['+971522233989', '+971501234567'],
                    'format_info': 'UAE mobile numbers start with "5" after the country code',
                    'local_format': 'Local format: 05XXXXXXXX',
                    'international_format': 'International format: +971XXXXXXXX' 
                }
                
            # Add detailed logs for debugging
            if is_developer_mode():
                response['debug'] = {
                    'to_number': sanitized_number,
                    'original_input': original_number,
                    'processed_number': phone_number,
                    'message_length': len(message),
                    'timestamp': datetime.now().isoformat()
                }
                
            return jsonify(response), 400
            
    except Exception as e:
        error_message = str(e)
        logger.error(f"Exception in send_sms endpoint: {error_message}")
        
        return jsonify({
            'success': False, 
            'error': 'Server error processing SMS request',
            'details': error_message if is_developer_mode() else 'See server logs for details',
            'traceback': traceback.format_exc() if is_developer_mode() else None
        }), 500

@app.route('/api/send-sms-alert', methods=['POST'])
def send_sms_alert():
    """Send a pre-formatted SMS alert notification"""
    if not is_developer_mode():
        return jsonify({
            'success': False, 
            'error': 'Not authorized',
            'solution': 'Enable developer mode to use SMS features'
        }), 403
        
    try:
        data = request.json
        phone_number = data.get('phone_number')
        alert_type = data.get('alert_type')
        
        if not phone_number or not alert_type:
            return jsonify({
                'success': False, 
                'error': 'Phone number and alert type are required',
                'required_fields': {
                    'phone_number': 'Recipient phone number in E.164 format (+971XXXXXXXXX)',
                    'alert_type': 'Type of alert to send (emotion_detected, face_recognized, system_status)'
                }
            }), 400
            
        # Initialize Twilio handler
        twilio_handler = TwilioHandler()
        
        # Check if Twilio is available
        if not twilio_handler.is_available():
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
        
        # Log the attempt with sanitized number (show only first 6 digits)
        sanitized_number = phone_number[:6] + "XXXX" if len(phone_number) > 6 else "XXXXXX"
        logger.info(f"Attempting to send SMS alert ({alert_type}) to {sanitized_number}...")
        
        # Prepare real-time data for alerts
        system_status = {}
        uptime = "Unknown"  # Default value
        if alert_type == 'system_status':
            # Get actual system uptime
            if core_launcher:
                uptime = core_launcher.get_uptime()
                system_status = core_launcher.get_system_status()
                if not isinstance(system_status, dict):
                    system_status = {}
            
        # Get the current emotion data if it's an emotion alert
        emotion_data = {}
        if alert_type == 'emotion_detected':
            # Get the most recent emotion
            recent_emotions = emotion_tracker.get_emotion_history(days=1)
            if recent_emotions and 'data' in recent_emotions and len(recent_emotions['data']) > 0:
                latest = recent_emotions['data'][0]
                emotion_data = {
                    'emotion': latest.get('emotion', 'happiness'),
                    'confidence': latest.get('intensity', 85) * 100,
                    'timestamp': latest.get('timestamp', datetime.now().isoformat())
                }
            
        # Get face recognition data if it's a face recognition alert
        face_data = {}
        if alert_type == 'face_recognized':
            # Get the most recent face recognition
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name, timestamp FROM recognition_history ORDER BY timestamp DESC LIMIT 1")
            result = cursor.fetchone()
            if result:
                face_data = {
                    'name': result[0],
                    'time': result[1]
                }
            
        # Prepare alert message based on type
        result = None
        if alert_type == 'emotion_detected':
            result = twilio_handler.send_notification(
                phone_number, 
                'emotion', 
                emotion=emotion_data.get('emotion', 'happiness'), 
                confidence=emotion_data.get('confidence', 85)
            )
        elif alert_type == 'face_recognized':
            result = twilio_handler.send_notification(
                phone_number, 
                'face', 
                name=face_data.get('name', 'User'), 
                time=face_data.get('time', 'just now')
            )
        elif alert_type == 'system_status':
            message = f'Robin AI system status: Online, uptime: {uptime}'
            if system_status:
                message += f"\nEmotion entries: {system_status.get('emotion_entries', 0)}"
                message += f"\nFace profiles: {system_status.get('face_profiles', 0)}"
                message += f"\nSessions: {system_status.get('sessions', 0)}"
                
            result = twilio_handler.send_notification(
                phone_number, 
                'system', 
                message=message
            )
        else:
            return jsonify({
                'success': False, 
                'error': 'Invalid alert type', 
                'valid_types': ['emotion_detected', 'face_recognized', 'system_status']
            }), 400
            
        if result and result.get('success', False):
            # Log success but with sanitized number for privacy
            logger.info(f"Successfully sent SMS alert ({alert_type}) to {sanitized_number}")
            
            return jsonify({
                'success': True,
                'message': f'Alert notification sent to {phone_number}',
                'sid': result.get('sid', ''),
                'timestamp': datetime.now().isoformat(),
                'alert_type': alert_type,
                'sent_to': phone_number
            })
        else:
            # Extract error details from the result
            error_message = result.get('error', 'Failed to send alert notification')
            solution = result.get('solution', '')
            details = result.get('details', '')
            
            # Log the error
            logger.error(f"SMS alert sending failed: {error_message}")
            if details:
                logger.error(f"SMS alert error details: {details}")
            
            # Create error response
            response = {
                'success': False,
                'error': error_message,
                'to': phone_number,
                'alert_type': alert_type
            }
            
            # Add optional fields if available
            if solution:
                response['solution'] = solution
                logger.info(f"SMS alert error solution: {solution}")
            if details:
                response['details'] = details
            
            # If this is a trial account issue with unverified number, provide specific guidance
            if "trial account" in error_message.lower() or "21612" in details:
                response['trial_account_help'] = "Your Twilio account is in trial mode. You can only send messages to verified numbers. Please verify this number in your Twilio console."
                
            # Add UAE-specific help if relevant
            if (phone_number.startswith('+971') or 
                phone_number.startswith('971') or 
                phone_number.startswith('05')):
                response['uae_format_help'] = "UAE mobile numbers should be in format +971xxxxxxxxx (e.g., +971522233989)"
                
            return jsonify(response), 500
            
    except Exception as e:
        logger.error(f"Error sending SMS alert: {str(e)}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/get-sms-status')
def get_sms_status():
    """Get SMS notification status"""
    if not is_developer_mode():
        return jsonify({
            'success': False, 
            'error': 'Not authorized',
            'solution': 'Enable developer mode to access SMS features'
        }), 403
        
    try:
        # Initialize Twilio handler
        twilio_handler = TwilioHandler()
        
        # Check if Twilio is available
        available = twilio_handler.is_available()
        
        # Get missing environment variables if not available
        missing_env_vars = []
        if not available:
            if not os.environ.get("TWILIO_ACCOUNT_SID"):
                missing_env_vars.append("TWILIO_ACCOUNT_SID")
            if not os.environ.get("TWILIO_AUTH_TOKEN"):
                missing_env_vars.append("TWILIO_AUTH_TOKEN")
            if not os.environ.get("TWILIO_PHONE_NUMBER"):
                missing_env_vars.append("TWILIO_PHONE_NUMBER")
        
        # Format phone number for display if available
        phone_number = os.environ.get('TWILIO_PHONE_NUMBER', '')
        formatted_phone = None
        
        if phone_number:
            # Format for UAE numbers specifically
            if phone_number.startswith('+971'):
                formatted_phone = f"{phone_number[:4]} {phone_number[4:6]} {phone_number[6:9]} {phone_number[9:]}"
            else:
                # Add spaces for readability
                formatted_phone = ' '.join([phone_number[i:i+4] for i in range(0, len(phone_number), 4)])
        
        response = {
            'success': True,
            'available': available,
            'account_sid': os.environ.get('TWILIO_ACCOUNT_SID', '')[:8] + '...' if available else '',
            'phone_number': phone_number,
            'formatted_phone': formatted_phone,
            'last_check': datetime.now().isoformat()
        }
        
        # Add missing credentials info if not available
        if not available:
            response['missing_credentials'] = missing_env_vars
            response['setup_instructions'] = "To setup SMS notifications, you need to set the Twilio environment variables and restart the server."
            
            # Provide more specific instructions for each missing variable
            if "TWILIO_ACCOUNT_SID" in missing_env_vars:
                response['twilio_account_sid_help'] = "Find your Account SID in the Twilio Console Dashboard at https://www.twilio.com/console"
                
            if "TWILIO_AUTH_TOKEN" in missing_env_vars:
                response['twilio_auth_token_help'] = "Find your Auth Token in the Twilio Console Dashboard at https://www.twilio.com/console"
                
            if "TWILIO_PHONE_NUMBER" in missing_env_vars:
                response['twilio_phone_number_help'] = "Get a Twilio phone number in the Twilio Console at https://www.twilio.com/console/phone-numbers/incoming"
        else:
            # Add account status if available
            response['account_type'] = 'Trial' if phone_number and phone_number.startswith('+1') else 'Production'
            response['verified_numbers_required'] = response['account_type'] == 'Trial'
            
            # Add tip for UAE numbers
            response['uae_format_tip'] = "For UAE recipients, use format +971XXXXXXXXX (e.g., +971522233989)"
            
        return jsonify(response)
            
    except Exception as e:
        logger.error(f"Error getting SMS status: {str(e)}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/get-sms-history')
def get_sms_history():
    """Get SMS message history"""
    if not is_developer_mode():
        return jsonify({
            'success': False, 
            'error': 'Not authorized',
            'solution': 'Enable developer mode to access SMS history'
        }), 403
        
    try:
        # Initialize Twilio handler
        twilio_handler = TwilioHandler()
        
        # Check if Twilio is available first
        if not twilio_handler.is_available():
            missing_env_vars = []
            if not os.environ.get("TWILIO_ACCOUNT_SID"):
                missing_env_vars.append("TWILIO_ACCOUNT_SID")
            if not os.environ.get("TWILIO_AUTH_TOKEN"):
                missing_env_vars.append("TWILIO_AUTH_TOKEN")
            if not os.environ.get("TWILIO_PHONE_NUMBER"):
                missing_env_vars.append("TWILIO_PHONE_NUMBER")
            
            return jsonify({
                'success': False,
                'error': 'Twilio service is not available',
                'missing_credentials': missing_env_vars,
                'setup_instructions': 'Set up Twilio credentials to access SMS history',
                'history': [] # Empty history since Twilio is not available
            })
        
        # Get message history
        logger.info("Fetching SMS message history from Twilio")
        messages = twilio_handler.get_message_history()
        
        # Format messages for display with better information
        history = []
        
        if messages:
            for msg in messages:
                # Sanitize phone number for privacy in logs (show only first 6 digits)
                to_number = msg.get('to', 'Unknown')
                sanitized_number = to_number[:6] + "XXXX" if len(to_number) > 6 else "XXXXXX"
                
                # Format the message body (truncate if too long)
                body = msg.get('body', '')
                if len(body) > 50:
                    body_preview = body[:50] + "..."
                else:
                    body_preview = body
                
                # Parse timestamp if available
                timestamp = msg.get('date_sent', '')
                formatted_time = timestamp
                
                if timestamp:
                    try:
                        # Try to parse and format the timestamp
                        from datetime import datetime
                        if isinstance(timestamp, str):
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception as e:
                        logger.error(f"Error formatting timestamp: {str(e)}")
                
                # Add to history with enhanced details
                history.append({
                    'to_number': to_number,
                    'sanitized_number': sanitized_number,
                    'status': msg.get('status', 'unknown'),
                    'body': body,
                    'body_preview': body_preview,
                    'timestamp': timestamp,
                    'formatted_time': formatted_time,
                    'sid': msg.get('sid', ''),
                    'price': msg.get('price', 'unknown'),
                    'direction': msg.get('direction', 'outbound'),
                    'error_code': msg.get('error_code', None)
                })
                
            logger.info(f"Retrieved {len(history)} SMS message records")
        else:
            logger.info("No SMS history found or message history is not available")
            
        # Additional metadata for the response
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID', '')[:8] + '...' if os.environ.get('TWILIO_ACCOUNT_SID') else ''
        phone_number = os.environ.get('TWILIO_PHONE_NUMBER', '')
            
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history),
            'retrieved_at': datetime.now().isoformat(),
            'from_number': phone_number,
            'account_sid': account_sid
        })
            
    except Exception as e:
        logger.error(f"Error getting SMS history: {str(e)}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'traceback': traceback.format_exc(),
            'history': [] # Empty history since an error occurred
        }), 500

@app.route('/api/set-consent', methods=['POST'])
def set_consent():
    """Set user consent for data storage"""
    try:
        data = request.json
        consent = data.get('consent', False)
        language = data.get('language', 'en')

        # Store consent in database
        db_manager.set_setting('user_consent', 'true' if consent else 'false')

        # Store language in database if provided
        if language:
            db_manager.set_setting('language_preference', language)

            # Set in session
            from flask import session
            session['language'] = language

        return jsonify({
            'success': True,
            'message': 'Consent preference saved successfully'
        })

    except Exception as e:
        logger.error(f"Error setting consent: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    """Update user profile during onboarding"""
    try:
        data = request.json

        # Required fields
        full_name = data.get('full_name')
        language_preference = data.get('language_preference', 'en')

        if not full_name:
            return jsonify({'success': False, 'error': 'Full name is required'}), 400

        # Optional fields with defaults
        age = data.get('age')
        nickname = data.get('nickname', full_name.split()[0] if full_name else 'User')
        voice_style = data.get('voice_style', 'default')
        theme = data.get('theme', 'dark')
        onboarding_complete = data.get('onboarding_complete', True)

        # Prepare profile data
        profile_data = {
            'full_name': full_name,
            'nickname': nickname,
            'language': language_preference,
            'voice_style': voice_style,
            'theme': theme,
            'age': age if age else None
        }

        # Use the ProfileManager to update the profile and infer personality
        success = profile_manager.update_profile(profile_data)

        if not success:
            return jsonify({'success': False, 'error': 'Failed to update profile'}), 500

        # Also maintain compatibility with old settings storage
        db_manager.set_setting('user_full_name', full_name)

        if age:
            db_manager.set_setting('user_age', str(age))

        db_manager.set_setting('user_nickname', nickname)
        db_manager.set_setting('preferred_voice_style', voice_style)
        db_manager.set_setting('theme', theme)
        db_manager.set_setting('language_preference', language_preference)
        db_manager.set_setting('onboarding_complete', 'true' if onboarding_complete else 'false')

        # Set the current session language
        from flask import session
        session['language'] = language_preference

        # Get the inferred personality for the response
        current_profile = profile_manager.get_current_profile()
        inferred_tone = current_profile.get('preferred_tone', 'neutral')

        # Create a personalized greeting based on the inferred personality
        greeting = profile_manager.get_greeting(nickname, language_preference)

        # Use the personalized TTS for the greeting
        tts_voice = profile_manager.get_tts_voice_for_language(language_preference)
        tts_manager.speak(greeting, tts_voice, language_preference, profile_manager)

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'greeting': greeting,
            'inferred_tone': inferred_tone
        })

    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/log-recognition', methods=['POST'])
def log_recognition():
    try:
        data = request.json
        name = data.get('name')
        emotion = data.get('emotion', 'neutral')
        confidence = data.get('confidence', 0.0)

        if not name:
            return jsonify({'success': False, 'error': 'Name is required'}), 400

        # Update last seen timestamp
        face_detector._update_last_seen(name)

        # Get session ID for logging
        from flask import session
        session_id = session.get('session_id', None)
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id

        # Log the emotion with session ID
        emotion_tracker.log_emotion(emotion, f"Face recognition: {name}", source="face", session_id=session_id)

        # Update profile interactions count
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        # Get the metadata
        cursor.execute("SELECT metadata FROM faces WHERE name = ?", (name,))
        result = cursor.fetchone()

        if result and result[0]:
            try:
                metadata = json.loads(result[0])

                # Update interactions count
                interactions = metadata.get('interactions', 0)
                metadata['interactions'] = interactions + 1

                # Update recognition rate (simulate improvement over time)
                current_rate = metadata.get('recognition_rate', 70)
                confidence_value = int(confidence * 100)
                new_rate = min(98, int((current_rate * 3 + confidence_value) / 4))
                metadata['recognition_rate'] = new_rate

                # Save updated metadata
                cursor.execute(
                    "UPDATE faces SET metadata = ? WHERE name = ?",
                    (json.dumps(metadata), name)
                )
                conn.commit()
            except Exception as e:
                logger.error(f"Error updating profile metadata: {str(e)}")

        # Log to recognition history table
        try:
            # Create table if it doesn't exist (not needed as we already created it in the DB schema)
            # We'll just use the existing recognition_history table

            # Add record with session_id
            timestamp = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO recognition_history (name, timestamp, confidence, emotion, session_id) VALUES (?, ?, ?, ?, ?)",
                (name, timestamp, confidence, emotion, session_id)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Error logging recognition to history: {str(e)}")

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error logging recognition: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def auto_learn_emotions():
    """Schedule function to run auto-learning cycles"""
    logger.info("Starting scheduled auto-learning cycle...")

    # Check if auto-learning should run
    if auto_learning.should_learn():
        # Run the learning cycle
        success = auto_learning.learn()

        # Also retrain the emotion model
        emotion_tracker.retrain_model()

        logger.info(f"Auto-learning cycle complete. Success: {success}")
    else:
        logger.info("Skipping auto-learning cycle (not time yet or disabled)")

@app.route('/api/auto-learning/status')
def get_auto_learning_status():
    """Get auto-learning status and metrics"""
    # Only accessible in developer mode
    if not is_developer_mode():
        return jsonify({'error': 'Developer mode required'}), 403

    status = auto_learning.get_learning_status()
    return jsonify(status)

@app.route('/api/auto-learning/toggle', methods=['POST'])
def toggle_auto_learning():
    """Enable or disable auto-learning"""
    # Only accessible in developer mode
    if not is_developer_mode():
        return jsonify({'error': 'Developer mode required'}), 403

    data = request.json
    enabled = data.get('enabled', True)

    new_state = auto_learning.set_learning_enabled(enabled)
    return jsonify({'success': True, 'enabled': new_state})

@app.route('/api/auto-learning/trigger', methods=['POST'])
def trigger_auto_learning():
    """Manually trigger an auto-learning cycle"""
    # Only accessible in developer mode
    if not is_developer_mode():
        return jsonify({'error': 'Developer mode required'}), 403

    success = auto_learning.learn()
    return jsonify({'success': success})

# Start the scheduler for auto-learning
def init_scheduler():
    scheduler.add_job(
        auto_learn_emotions, 
        'interval', 
        hours=12, 
        next_run_time=datetime.now() + timedelta(minutes=10)
    )
    scheduler.start()
    logger.info("Auto-learning scheduler initialized")

# Make sure database is initialized at module import time
db_manager.initialize_db()

# Initialize profile manager tables
profile_manager.initialize_tables()

# Mobile app routes
@app.route('/mobile')
@app.route('/mobile/splash')
def mobile_splash():
    """Mobile app splash screen"""
    # Splash screen is the entry point for mobile experience
    return render_template('mobile/splash.html', versioned_url=versioned_url)

@app.route('/mobile/index')
def mobile_index():
    """Mobile app main page"""
    # Mobile interface is always accessible without onboarding checks
    return render_template('mobile/index.html', versioned_url=versioned_url)

@app.route('/mobile/emotions')
def mobile_emotions():
    """Mobile app emotions page"""
    return render_template('mobile/emotions.html', versioned_url=versioned_url)

@app.route('/mobile/help')
def mobile_help():
    """Mobile app help page."""
    return render_template('mobile/help.html', versioned_url=versioned_url)

@app.route('/mobile/contact')
def mobile_contact():
    """Mobile app contact page."""
    return render_template('mobile/contact.html', versioned_url=versioned_url)

@app.route('/mobile/profiles')
def mobile_profiles():
    """Mobile app profiles page"""
    return render_template('mobile/profiles.html', versioned_url=versioned_url)

@app.route('/mobile/settings')
def mobile_settings():
    """Mobile app settings page"""
    return render_template('mobile/settings.html', versioned_url=versioned_url)

@app.route('/ai-models')
def ai_models_page():
    """AI Models status and testing page"""
    return render_template('ai_models.html', versioned_url=versioned_url)
    
# User settings API endpoints
@app.route('/api/user/settings', methods=['GET'])
def user_settings():
    """Get or update user settings"""
    try:
        if request.method == 'GET':
            # Get current settings from the database
            settings = {}
            default_settings = {
                'language': 'en',
                'darkMode': True,
                'voiceStyle': 'default',
                'voiceRecognition': True,
                'storeHistory': True,
                'faceRecognition': True,
                'aiModelBackend': os.environ.get('MODEL_BACKEND', 'auto'),
                'developerMode': is_developer_mode(),
                'debugMode': os.environ.get('DEBUG', 'false').lower() == 'true'
            }
            
            # Get values from database or use defaults
            for key, default_value in default_settings.items():
                try:
                    value = db_manager.get_setting(key, str(default_value))
                    
                    # Convert string to proper types
                    if isinstance(default_value, bool):
                        # Handle string to boolean conversion
                        if isinstance(value, str):
                            settings[key] = value.lower() in ['true', '1', 'yes']
                        else:
                            settings[key] = bool(value)
                    else:
                        settings[key] = value
                except Exception as e:
                    logger.warning(f"Error getting setting {key}: {str(e)}")
                    settings[key] = default_value
            
            return jsonify({
                'success': True,
                'settings': settings
            })
        
        # Handle POST request (update settings)
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Update only the specified settings
        updated_settings = {}
        for key, value in data.items():
            try:
                # Special handling for certain settings
                if key == 'developerMode':
                    # Only set developer mode if authorized
                    if value and not is_developer_mode():
                        if request.headers.get('X-Developer-Key') != os.environ.get('DEVELOPER_KEY', 'robin_dev_key'):
                            continue  # Skip unauthorized developer mode enable
                    set_developer_mode(value)
                    updated_settings[key] = value
                elif key == 'debugMode':
                    # Only allow debug mode changes in developer mode
                    if is_developer_mode():
                        # Set in database
                        db_manager.set_setting(key, str(value))
                        # Try to update environment variable too
                        os.environ['DEBUG'] = 'true' if value else 'false'
                        updated_settings[key] = value
                elif key == 'aiModelBackend':
                    # Update both database and environment
                    db_manager.set_setting(key, str(value))
                    os.environ['MODEL_BACKEND'] = str(value)
                    updated_settings[key] = value
                else:
                    # Standard setting
                    db_manager.set_setting(key, str(value))
                    updated_settings[key] = value
            except Exception as e:
                logger.error(f"Error updating setting {key}: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f"Error updating setting {key}: {str(e)}"
                }), 500
        
        return jsonify({
            'success': True,
            'updated': updated_settings
        })
        
    except Exception as e:
        logger.error(f"Error managing user settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user/settings/reset', methods=['POST'])
def reset_user_settings():
    """Reset user settings to default"""
    try:
        # Default settings
        default_settings = {
            'language': 'en',
            'darkMode': True,
            'voiceStyle': 'default',
            'voiceRecognition': True,
            'storeHistory': True,
            'faceRecognition': True,
            'aiModelBackend': 'auto',
        }
        
        # Don't reset developer mode or debug mode
        preserve_settings = ['developerMode', 'debugMode']
        
        # Get current values of preserved settings
        preserved_values = {}
        for key in preserve_settings:
            try:
                preserved_values[key] = db_manager.get_setting(key, 'false')
            except:
                preserved_values[key] = 'false'
        
        # Delete all settings first
        try:
            db_manager.execute_query("DELETE FROM settings WHERE key NOT IN %s", (tuple(preserve_settings),))
        except Exception as e:
            logger.warning(f"Error deleting settings: {str(e)}")
        
        # Then insert default settings
        for key, value in default_settings.items():
            db_manager.set_setting(key, str(value))
        
        # Restore preserved settings
        for key, value in preserved_values.items():
            db_manager.set_setting(key, value)
        
        # Update MODEL_BACKEND environment variable
        os.environ['MODEL_BACKEND'] = 'auto'
        
        return jsonify({
            'success': True,
            'message': 'Settings reset to default values'
        })
    except Exception as e:
        logger.error(f"Error resetting user settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user/logout', methods=['POST'])
def user_logout():
    """Log out the current user"""
    try:
        # Clear session data
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
    except Exception as e:
        logger.error(f"Error logging out: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/test-ask')
def test_ask_endpoint():
    """Test page for the /ask endpoint"""
    # Only accessible in developer mode
    if not is_developer_mode():
        return redirect(url_for('mobile_index'))
        
    return render_template('test_ask_endpoint.html')

# SMS Notification Routes - duplicate code removed

@app.route('/api/send-sms-legacy', methods=['POST'])
def send_sms_legacy():
    """Send SMS notification (legacy route)"""
    # Only allow in developer mode
    if not is_developer_mode():
        return jsonify({'success': False, 'error': 'Developer mode required'}), 403
    
    # Get request parameters
    data = request.json
    # Support both parameter names for backward compatibility
    phone_number = data.get('phone_number', data.get('to_number'))
    message = data.get('message')
    
    if not phone_number or not message:
        return jsonify({'success': False, 'error': 'Phone number and message are required'}), 400
    
    # Check if SMS service is available
    if not twilio_handler.is_available():
        return jsonify({'success': False, 'error': 'SMS service is not available. Check Twilio credentials.'}), 503
    
    # Send the SMS
    try:
        result = twilio_handler.send_message(phone_number, message)
        
        if result and result.get('success', False):
            return jsonify({'success': True, 'message': 'SMS sent successfully'})
        else:
            # Extract error details from the result
            error_message = result.get('error', 'Failed to send SMS')
            solution = result.get('solution', '')
            details = result.get('details', '')
            
            response = {
                'success': False,
                'error': error_message
            }
            
            # Add optional fields if available
            if solution:
                response['solution'] = solution
            if details:
                response['details'] = details
                
            return jsonify(response), 500
            
    except Exception as e:
        logger.error(f"SMS sending error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/send-sms-alert-legacy', methods=['POST'])
def send_sms_alert_legacy():
    """Send a pre-formatted SMS alert notification (legacy route)"""
    # Only allow in developer mode
    if not is_developer_mode():
        return jsonify({'success': False, 'error': 'Developer mode required'}), 403
    
    # Get request parameters
    data = request.json
    # Support both parameter names for backward compatibility
    phone_number = data.get('phone_number', data.get('to_number'))
    notification_type = data.get('alert_type', 'alert')  # Default to alert type
    message = data.get('message', 'Alert notification')
    
    if not phone_number:
        return jsonify({'success': False, 'error': 'Phone number is required'}), 400
    
    # Check if SMS service is available
    if not twilio_handler.is_available():
        return jsonify({'success': False, 'error': 'SMS service is not available. Check Twilio credentials.'}), 503
    
    # Prepare notification parameters
    notification_params = {'message': message}
    
    # Add additional parameters
    alert_level = data.get('alert_level')
    if alert_level:
        notification_params['level'] = alert_level
    
    # Add emotion details if this is an emotion alert
    if notification_type == 'emotion_detected':
        notification_params['emotion'] = data.get('emotion', 'unknown')
        notification_params['confidence'] = data.get('confidence', 90)
    
    # Add face details if this is a face recognition alert
    if notification_type == 'face_recognized':
        notification_params['name'] = data.get('name', 'someone')
        notification_params['time'] = data.get('time', 'just now')
    
    # Send the notification
    try:
        result = twilio_handler.send_notification(phone_number, notification_type.split('_')[0], **notification_params)
        
        if result and result.get('success', False):
            return jsonify({'success': True, 'message': f'Alert notification sent successfully'})
        else:
            # Extract error details from the result
            error_message = result.get('error', 'Failed to send notification')
            solution = result.get('solution', '')
            details = result.get('details', '')
            
            response = {
                'success': False,
                'error': error_message
            }
            
            # Add optional fields if available
            if solution:
                response['solution'] = solution
            if details:
                response['details'] = details
                
            return jsonify(response), 500
            
    except Exception as e:
        logger.error(f"SMS notification error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == "__main__":
    # Start scheduler
    init_scheduler()

    # Launch core systems in a separate thread
    threading.Thread(target=core_launcher.start).start()

    # Wait for core systems to initialize
    time.sleep(2)

    # Start Flask app when run directly (not through Gunicorn)
    # This ensures proper binding for both development and deployment
    port = 5000
    try:
        logger.info(f"Starting Flask app on port {port}")
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
    except OSError as e:
        if "Address already in use" in str(e):
            # Fallback to alternative port if 5000 is in use
            port = 8000
            logger.info(f"Port 5000 unavailable, falling back to port {port}")
            app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
        else:
            # Re-raise other OSErrors
            raise
