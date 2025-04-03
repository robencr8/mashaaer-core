import os
import logging
import json
from flask import Flask, render_template, request, jsonify, Response, redirect, url_for
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
import twilio_api

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "robin_ai_default_secret")
# Enable CORS for all routes to support Flutter and mobile app integration
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize components
config = Config()
db_manager = DatabaseManager(config=config, db_path=config.DB_PATH)
emotion_tracker = EmotionTracker(db_manager)
tts_manager = TTSManager(config)
intent_classifier = IntentClassifier()
voice_recognition = VoiceRecognition(config)
face_detector = FaceDetector(config, db_manager)
auto_learning = AutoLearning(db_manager)
# Note: Twilio API is imported directly as needed
from profile_manager import ProfileManager
profile_manager = ProfileManager(db_manager)

# Initialize API routes
from api_routes import init_api
init_api(app, db_manager, emotion_tracker, face_detector, 
         tts_manager, voice_recognition, intent_classifier, config)

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

@app.before_request
def log_request_info():
    if request.path.startswith('/api/'):
        # Log API requests with more detail
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
    else:
        # Simple logging for regular routes
        print(f"🔍 Request to: {request.path}")
    # No need to return anything from this before_request handler

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
    # Check if onboarding has been completed
    onboarding_status = db_manager.get_setting('onboarding_complete', 'false')
    onboarding_complete = False

    if isinstance(onboarding_status, str):
        onboarding_complete = onboarding_status.lower() == 'true'

    # If onboarding not complete, redirect to startup
    if not onboarding_complete:
        return redirect(url_for('startup'))

    dev_mode = is_developer_mode()
    return render_template('index.html', dev_mode=dev_mode)

@app.route('/startup')
def startup():
    welcome_message_en = "Welcome to Mashaaer Feelings. Create the future, I'm listening."
    welcome_message_ar = "مرحبًا بك في مشاعر. اصنع المستقبل، أنا أسمعك."
    
    # Play both languages for maximum accessibility
    try:
        tts_manager.speak(welcome_message_en, 'default', 'en-US', profile_manager)
        tts_manager.speak(welcome_message_ar, 'arabic', 'ar', profile_manager)
    except Exception as e:
        logger.error(f"Error speaking welcome message: {str(e)}")
    
    # Check if interactive splash screen is enabled
    interactive_splash = os.environ.get('INTERACTIVE_SPLASH', 'true').lower() == 'true'
    
    if interactive_splash:
        return render_template('interactive_cosmic_splash.html')
    else:
        # Check if cosmic onboarding is enabled
        cosmic_onboarding = os.environ.get('COSMIC_ONBOARDING', 'true').lower() == 'true'
        
        if cosmic_onboarding:
            return render_template('cosmic_onboarding.html')
        else:
            return render_template('startup_standalone.html')
        
@app.route('/interactive-splash')
def interactive_splash():
    """Interactive splash screen with animated cosmic sphere"""
    welcome_message_ar = "مرحبًا بك في مشاعر. اصنع المستقبل، أنا أسمعك."
    
    # Play welcome message in Arabic as default
    try:
        tts_manager.speak(welcome_message_ar, 'arabic', 'ar', profile_manager)
    except Exception as e:
        logger.error(f"Error speaking welcome message: {str(e)}")
    
    return render_template('interactive_cosmic_splash.html')

@app.route('/api/play-cosmic-sound', methods=['POST'])
def play_cosmic_sound():
    """Play a cosmic sound effect and get voice feedback"""
    sound_type = request.json.get('sound_type', 'click')
    
    try:
        # Different sound effects for different interactions
        sound_file = 'click.mp3'
        if sound_type == 'hover':
            sound_file = 'hover.mp3'
        elif sound_type == 'ambient':
            sound_file = 'cosmic_ambient.mp3'
        elif sound_type == 'welcome':
            sound_file = 'welcome.mp3'
            
            # For welcome sound, also play voice greeting
            language = request.json.get('language', 'ar')
            if language == 'ar':
                welcome_message = "مرحبًا بك في مشاعر. اصنع المستقبل، أنا أسمعك."
                tts_manager.speak(welcome_message, 'arabic', 'ar', profile_manager)
            else:
                welcome_message = "Welcome to Mashaaer Feelings. Create the future, I'm listening."
                tts_manager.speak(welcome_message, 'default', 'en-US', profile_manager)
        
        # Return sound file path 
        sound_path = f'/static/audio/{sound_file}'
        
        return jsonify({
            'success': True,
            'sound_path': sound_path
        })
    except Exception as e:
        logger.error(f"Error playing cosmic sound: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/cosmic-onboarding')
def cosmic_onboarding():
    """Cosmic onboarding experience with voice interaction"""
    welcome_message_ar = "مرحبًا بك في مشاعر. اصنع المستقبل، أنا أسمعك."
    
    # Play welcome message in Arabic as default
    try:
        tts_manager.speak(welcome_message_ar, 'arabic', 'ar', profile_manager)
    except Exception as e:
        logger.error(f"Error speaking welcome message: {str(e)}")
    
    return render_template('cosmic_onboarding.html')

@app.route('/consent')
def consent():
    return render_template('consent.html')

@app.route('/voice-register')
def voice_register():
    return render_template('voice_register.html')

@app.route('/goodbye')
def goodbye():
    return render_template('goodbye.html')

@app.route('/demo')
def demo():
    dev_mode = is_developer_mode()
    return render_template('demo.html', dev_mode=dev_mode)

@app.route('/emotion-timeline')
def emotion_timeline():
    emotions = emotion_tracker.get_emotion_history()
    dev_mode = is_developer_mode()
    return render_template('emotion_timeline.html', emotions=emotions, dev_mode=dev_mode)

@app.route('/profile')
def profile():
    profiles = face_detector.get_all_profiles()
    dev_mode = is_developer_mode()
    return render_template('profile.html', profiles=profiles, dev_mode=dev_mode)

@app.route('/live-view')
def live_view():
    dev_mode = is_developer_mode()
    return render_template('live_view.html', dev_mode=dev_mode)

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
        return redirect(url_for('index'))

    # Get AI learning stats
    learning_status = auto_learning.get_learning_status()
    
    # Check Twilio availability using our new API
    import twilio_api
    sms_available = twilio_api.is_twilio_configured()

    system_stats = {
        'uptime': core_launcher.get_uptime(),
        'memory_size': db_manager.get_db_size(),
        'emotion_count': emotion_tracker.get_total_entries(),
        'face_profiles': face_detector.get_profile_count(),
        'system_status': core_launcher.get_system_status(),
        'learning_status': learning_status,
        'sms_available': sms_available
    }

    return render_template('admin.html', stats=system_stats, dev_mode=True)

@app.route('/sms-notifications')
def sms_notifications():
    # Only accessible in developer mode
    if not is_developer_mode():
        return redirect(url_for('index'))
    
    # Import Twilio API helpers
    import twilio_api
    
    # Check if Twilio is available
    twilio_status = twilio_api.is_twilio_configured()
    
    # Get Twilio account information (truncated for security)
    twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID', '')
    twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER', '')
    
    # Get message history from Twilio API
    sms_history = twilio_api.get_message_history()
    
    # Prepare status message
    twilio_status_message = "SMS notifications are active and ready." if twilio_status else "SMS notifications unavailable. Check Twilio credentials."
    
    return render_template(
        'sms_notifications.html', 
        dev_mode=True,
        twilio_status=twilio_status,
        twilio_status_message=twilio_status_message,
        sms_history=sms_history
    )

@app.route('/session-report')
def session_report():
    """Show the session report dashboard with real-time data visualization"""
    dev_mode = is_developer_mode()

    # Get sample emotion labels and data for initial chart display
    emotion_labels = ['Happy', 'Sad', 'Angry', 'Surprised', 'Fearful', 'Disgusted', 'Neutral']
    emotion_data = [12, 5, 3, 7, 2, 1, 8]

    return render_template('session_report.html', 
                          dev_mode=dev_mode, 
                          labels=emotion_labels, 
                          data=emotion_data)

@app.route('/download/session.csv')
def download_session_csv():
    """Download session data as CSV"""
    from flask import session as flask_session
    import csv
    from io import StringIO

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
        WHERE session_id = ?
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

    # For onboarding demo, allow simulated responses if no audio provided
    if not audio_data:
        # In a real implementation, this would be rejected with a 400 error
        # But for the cosmic onboarding demo, we'll simulate a reasonable response
        logger.info("No audio data provided, using simulated response for onboarding")
        
        # Get some context about what we're listening for
        context = request.form.get('context', '')
        
        # Generate simulated responses for different contexts
        simulated_text = "نعم، أوافق"  # Default "Yes, I agree" in Arabic
        
        if 'name' in context.lower():
            simulated_text = "محمد أحمد"  # A common Arabic name
        elif 'nickname' in context.lower():
            simulated_text = "محمد"
        elif 'email' in context.lower():
            simulated_text = "example@email.com"
        elif 'terms' in context.lower() or 'agree' in context.lower():
            simulated_text = "نعم، أوافق"  # "Yes, I agree" in Arabic
        
        # Process with the simulated text
        emotion = emotion_tracker.analyze_text(simulated_text)
        intent = intent_classifier.classify(simulated_text)
        
        return jsonify({
            'success': True, 
            'text': simulated_text, 
            'emotion': emotion,
            'intent': intent,
            'simulated': True  # Flag to indicate this was a simulated response
        })

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
                greeting = "Welcome back, Roben. Mashaaer is fully operational."
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
            greeting = "Welcome back, Roben. Mashaaer is fully operational."
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
    emotions = emotion_tracker.get_emotion_history(days=days)
    return jsonify(emotions)

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

@app.route("/api/profile/<name>")
def get_profile(name):
    try:
        # Get profile by name
        profiles = face_detector.get_all_profiles()
        profile = next((p for p in profiles if p['name'] == name), None)

        if not profile:
            return jsonify({'success': False, 'error': 'Profile not found'}), 404

        # Add emotion data if available
        try:
            # Get the primary emotion from the emotion tracker
            profile['primary_emotion'] = emotion_tracker.get_primary_emotion_for_name(name)
        except:
            profile['primary_emotion'] = 'neutral'

        return jsonify({'success': True, 'profile': profile})
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/set-language', methods=['POST'])
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
    """Send SMS notification"""
    if not is_developer_mode():
        return jsonify({'success': False, 'error': 'Not authorized'}), 403
        
    try:
        data = request.json
        phone_number = data.get('phone_number')
        message = data.get('message')
        
        if not phone_number or not message:
            return jsonify({'success': False, 'error': 'Phone number and message are required'}), 400
            
        # Import Twilio API helpers
        import twilio_api
        
        # Check if Twilio is available
        if not twilio_api.is_twilio_configured():
            return jsonify({
                'success': False, 
                'error': 'Twilio service is not available. Check credentials.'
            }), 503
            
        # Send the message
        result = twilio_api.send_sms(phone_number, message)
        
        if result:
            return jsonify({
                'success': True,
                'message': f'SMS sent to {phone_number}',
                'sid': result.get('sid', '')
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send SMS'
            }), 500
            
    except Exception as e:
        logger.error(f"Error sending SMS: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/send-sms-alert', methods=['POST'])
def send_sms_alert():
    """Send a pre-formatted SMS alert notification"""
    if not is_developer_mode():
        return jsonify({'success': False, 'error': 'Not authorized'}), 403
        
    try:
        data = request.json
        phone_number = data.get('phone_number')
        alert_type = data.get('alert_type')
        
        if not phone_number or not alert_type:
            return jsonify({'success': False, 'error': 'Phone number and alert type are required'}), 400
            
        # Import Twilio API helpers
        import twilio_api
        
        # Check if Twilio is available
        if not twilio_api.is_twilio_configured():
            return jsonify({
                'success': False, 
                'error': 'Twilio service is not available. Check credentials.'
            }), 503
            
        # Prepare alert message based on type
        result = None
        title = ""
        message = ""
        level = "info"
        
        if alert_type == 'emotion_detected':
            title = "Emotion Detection"
            message = "An emotional response of 'happiness' was detected with 85% confidence."
            level = "info"
        elif alert_type == 'face_recognized':
            title = "Face Recognition"
            message = "User was recognized in the system just now."
            level = "info"
        elif alert_type == 'system_status':
            uptime = "3 hours, 45 minutes"
            title = "System Status"
            message = f"Mashaaer system is online. Current uptime: {uptime}"
            level = "info"
        elif alert_type == 'warning':
            title = "System Warning"
            message = "System resources are running low. Please check the admin dashboard."
            level = "warning"
        elif alert_type == 'alert':
            title = "Critical Alert"
            message = "Multiple recognition failures detected. System might need maintenance."
            level = "alert"
        else:
            return jsonify({'success': False, 'error': 'Invalid alert type'}), 400
            
        # Send the notification
        result = twilio_api.send_notification(phone_number, title, message, level)
            
        if result:
            return jsonify({
                'success': True,
                'message': f'Alert notification sent to {phone_number}',
                'sid': result.get('sid', '')
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send alert notification'
            }), 500
            
    except Exception as e:
        logger.error(f"Error sending SMS alert: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get-sms-status')
def get_sms_status():
    """Get SMS notification status"""
    if not is_developer_mode():
        return jsonify({'success': False, 'error': 'Not authorized'}), 403
        
    try:
        # Import Twilio API helpers
        import twilio_api
        
        # Check if Twilio is available
        available = twilio_api.is_twilio_configured()
        
        return jsonify({
            'success': True,
            'available': available,
            'account_sid': os.environ.get('TWILIO_ACCOUNT_SID', '')[:8] + '...' if available else '',
            'phone_number': os.environ.get('TWILIO_PHONE_NUMBER', '') if available else ''
        })
            
    except Exception as e:
        logger.error(f"Error getting SMS status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get-sms-history')
def get_sms_history():
    """Get SMS message history"""
    if not is_developer_mode():
        return jsonify({'success': False, 'error': 'Not authorized'}), 403
        
    try:
        # Import Twilio API helpers
        import twilio_api
        
        # Get message history
        messages = twilio_api.get_message_history()
        
        # Format messages for display (already in the correct format from twilio_api)
        history = []
        for msg in messages:
            history.append({
                'to_number': msg.get('to', 'Unknown'),
                'status': msg.get('sid', 'unknown'),
                'body': msg.get('message', ''),
                'timestamp': msg.get('timestamp', '')
            })
            
        return jsonify({
            'success': True,
            'history': history
        })
            
    except Exception as e:
        logger.error(f"Error getting SMS history: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cosmic-onboarding-profile', methods=['POST'])
def cosmic_onboarding_profile():
    """Update user profile during cosmic onboarding experience"""
    try:
        data = request.json
        
        # Get basic profile data
        full_name = data.get('full_name')
        nickname = data.get('nickname')
        language = data.get('language_preference', 'ar')
        
        # Store in session
        from flask import session
        session['language'] = language
        session['nickname'] = nickname
        session['full_name'] = full_name
        
        # Update the profile
        profile_data = {
            'full_name': full_name,
            'nickname': nickname,
            'language': language
        }
        
        # Update the user profile
        profile_manager.update_profile(profile_data)
        
        # Get appropriate voice for selected language
        tts_voice = profile_manager.get_tts_voice_for_language(language)
        
        # Create welcome message
        if language == 'ar':
            welcome_msg = f"مرحبًا بك يا {nickname} في مشاعر. أنا سعيد بوجودك معنا."
        else:
            welcome_msg = f"Welcome {nickname} to Mashaaer Feelings. I'm glad to have you with us."
        
        # Speak welcome message
        try:
            tts_manager.speak(welcome_msg, tts_voice, language, profile_manager)
        except Exception as e:
            logger.error(f"Error speaking welcome message: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'welcome_message': welcome_msg
        })
    
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/set-consent', methods=['POST'])
def set_consent():
    """Set user consent for data storage"""
    try:
        data = request.json
        consent = data.get('consent', False)
        language = data.get('language', 'en')
        interaction_mode = data.get('interaction_mode', 'text')  # New parameter for voice/text mode

        # Store consent in database
        db_manager.set_setting('user_consent', 'true' if consent else 'false')

        # Store language in database if provided
        if language:
            db_manager.set_setting('language_preference', language)

            # Set in session
            from flask import session
            session['language'] = language
            
        # Store interaction mode preference
        db_manager.set_setting('interaction_mode', interaction_mode)
        logger.info(f"User interaction mode set to: {interaction_mode}")
        
        # Enable or disable voice recognition based on interaction mode
        voice_enabled = (interaction_mode == 'voice')
        db_manager.set_setting('voice_recognition_enabled', 'true' if voice_enabled else 'false')

        return jsonify({
            'success': True,
            'message': 'Consent and preferences saved successfully'
        })

    except Exception as e:
        logger.error(f"Error setting consent: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/regular-update-profile', methods=['POST'])
def regular_update_profile():
    """Update user profile during standard onboarding"""
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
def mobile_splash():
    """Mobile app splash screen"""
    # Splash screen is the entry point for mobile experience
    return render_template('mobile/splash.html')

@app.route('/mobile/index')
def mobile_index():
    """Mobile app main page"""
    # Mobile interface is always accessible without onboarding checks
    return render_template('mobile/index.html')

@app.route('/mobile/emotions')
def mobile_emotions():
    """Mobile app emotions page"""
    return render_template('mobile/emotions.html')

@app.route('/mobile/help')
def mobile_help():
    """Mobile app help page."""
    return render_template('mobile/help.html')

@app.route('/mobile/contact')
def mobile_contact():
    """Mobile app contact page."""
    return render_template('mobile/contact.html')

@app.route('/mobile/profiles')
def mobile_profiles():
    """Mobile app profiles page"""
    return render_template('mobile/profiles.html')

@app.route('/mobile/settings')
def mobile_settings():
    """Mobile app settings page"""
    return render_template('mobile/settings.html')

@app.route('/api/user/settings', methods=['GET', 'POST'])
def user_settings():
    """Get or update user settings"""
    if request.method == 'GET':
        # Get settings from database
        settings = {
            'language': db_manager.get_setting('language', 'en'),
            'darkMode': db_manager.get_setting('dark_mode', 'true').lower() == 'true',
            'voiceStyle': db_manager.get_setting('voice_style', 'default'),
            'voiceRecognition': db_manager.get_setting('voice_recognition_enabled', 'true').lower() == 'true',
            'storeHistory': db_manager.get_setting('store_history', 'true').lower() == 'true',
            'faceRecognition': db_manager.get_setting('face_recognition_enabled', 'true').lower() == 'true'
        }
        return jsonify({'success': True, 'settings': settings})
    else:
        # Update settings
        data = request.json
        try:
            for key, value in data.items():
                if key == 'language':
                    db_manager.set_setting('language', value)
                elif key == 'darkMode':
                    db_manager.set_setting('dark_mode', 'true' if value else 'false')
                elif key == 'voiceStyle':
                    db_manager.set_setting('voice_style', value)
                elif key == 'voiceRecognition':
                    db_manager.set_setting('voice_recognition_enabled', 'true' if value else 'false')
                elif key == 'storeHistory':
                    db_manager.set_setting('store_history', 'true' if value else 'false')
                elif key == 'faceRecognition':
                    db_manager.set_setting('face_recognition_enabled', 'true' if value else 'false')
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error updating settings: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/user/settings/reset', methods=['POST'])
def reset_user_settings():
    """Reset user settings to default"""
    try:
        default_settings = {
            'language': 'en',
            'dark_mode': 'true',
            'voice_style': 'default',
            'voice_recognition_enabled': 'true',
            'store_history': 'true',
            'face_recognition_enabled': 'true'
        }

        for key, value in default_settings.items():
            db_manager.set_setting(key, value)

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error resetting settings: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/user/logout', methods=['POST'])
def user_logout():
    """Log out the current user"""
    try:
        # Clear the onboarding flag
        db_manager.set_setting('onboarding_complete', 'false')

        # Clear session data
        from flask import session
        session.clear()

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error logging out: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# SMS Notification Routes - duplicate code removed

@app.route('/api/send-sms-legacy', methods=['POST'])
def send_sms_legacy():
    """Send SMS notification (legacy route)"""
    # Only allow in developer mode
    if not is_developer_mode():
        return jsonify({'success': False, 'error': 'Developer mode required'}), 403
    
    # Get request parameters
    data = request.json
    to_number = data.get('to_number')
    message = data.get('message')
    
    if not to_number or not message:
        return jsonify({'success': False, 'error': 'Phone number and message are required'}), 400
    
    # Import Twilio API helpers
    import twilio_api
    
    # Check if SMS service is available
    if not twilio_api.is_twilio_configured():
        return jsonify({'success': False, 'error': 'SMS service is not available. Check Twilio credentials.'}), 503
    
    # Send the SMS
    try:
        result = twilio_api.send_sms(to_number, message)
        
        if result:
            return jsonify({'success': True, 'message': 'SMS sent successfully', 'sid': result.get('sid', '')})
        else:
            return jsonify({'success': False, 'error': 'Failed to send SMS'}), 500
            
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
    to_number = data.get('to_number')
    notification_type = data.get('alert_type', 'alert')  # Default to alert type
    message = data.get('message', 'Alert notification')
    
    if not to_number:
        return jsonify({'success': False, 'error': 'Phone number is required'}), 400
    
    # Import Twilio API helpers
    import twilio_api
    
    # Check if SMS service is available
    if not twilio_api.is_twilio_configured():
        return jsonify({'success': False, 'error': 'SMS service is not available. Check Twilio credentials.'}), 503
    
    # Prepare notification parameters
    title = notification_type.replace('_', ' ').title()
    level = data.get('alert_level', 'info')
    
    # Customize message based on notification type
    if notification_type == 'emotion_detected':
        emotion = data.get('emotion', 'unknown')
        confidence = data.get('confidence', 90)
        message = f"Emotion detected: {emotion} with {confidence}% confidence"
    elif notification_type == 'face_recognized':
        name = data.get('name', 'someone')
        time = data.get('time', 'just now')
        message = f"Face recognized: {name} was seen {time}"
    
    # Send the notification
    try:
        result = twilio_api.send_notification(to_number, title, message, level)
        
        if result:
            return jsonify({
                'success': True, 
                'message': 'Alert notification sent successfully',
                'sid': result.get('sid', '')
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to send notification'}), 500
            
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

    # Start Flask app
    app.run(host="0.0.0.0", port=3000, debug=True, use_reloader=False)